import uuid
import logging
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from .models import Donation
from .serializers import DonationSerializer, InitiateDonationSerializer
from .services.wompi import create_payment_session, verify_webhook_signature, get_transaction_by_reference
from .services.pdf_generator import generate_donation_certificate
from .services.email_service import send_donation_email

logger = logging.getLogger(__name__)


def procesar_transaccion_wompi(referencia: str, transaction_data: dict) -> Donation:
    """
    Aplica a una donación el resultado reportado por Wompi.

    Fuente única para el webhook y para la verificación manual del panel
    ("Verificar con Wompi"), garantizando idéntico comportamiento:
    - Idempotencia: si ya está completada, no reprocesa ni reenvía certificado.
    - Mapeo de estados APPROVED/DECLINED/VOIDED/ERROR.
    - Al pasar a completado, genera y envía el certificado; los errores de
      PDF/email se registran pero no propagan.

    Lanza Donation.DoesNotExist si la referencia no existe.
    """
    estado_map = {
        'APPROVED': 'completado',
        'DECLINED': 'fallido',
        'VOIDED': 'reembolsado',
        'ERROR': 'fallido',
    }

    # Seguridad: bloqueo pesimista + idempotencia (Wompi reenvía webhooks).
    with transaction.atomic():
        donation = Donation.objects.select_for_update().get(referencia=referencia)

        if donation.estado == 'completado':
            logger.info(
                f"Transacción idempotente: donación {referencia} ya completada, se omite reproceso."
            )
            return donation

        # --- Defensa en profundidad: verificación de monto ------------------
        # La firma del webhook autentica el ORIGEN del mensaje (Wompi), pero
        # NO garantiza que el monto reportado coincida con lo que esta
        # donación acordó. Si un monto alterado llegara a aprobarse, la
        # fundación emitiría un certificado por un valor no recaudado.
        monto_reportado = transaction_data.get('amount_in_cents')
        if monto_reportado is not None:
            from .services.wompi import _cop_a_centavos
            try:
                monto_esperado = _cop_a_centavos(donation.monto)
                if int(monto_reportado) != monto_esperado:
                    donation.revision_requerida = True
                    donation.wompi_response = transaction_data
                    donation.save(update_fields=['revision_requerida', 'wompi_response'])
                    logger.critical(
                        "Webhook con MONTO ALTERADO: donación %s esperaba %s "
                        "centavos y Wompi reportó %s. Marcada para revisión "
                        "manual; NO se aprobó ni se emitió certificado.",
                        referencia, monto_esperado, monto_reportado,
                    )
                    return donation
            except (TypeError, ValueError):
                logger.warning(
                    "Webhook con amount_in_cents no numérico para %s: %r",
                    referencia, monto_reportado,
                )

        nuevo_estado = estado_map.get(transaction_data.get('status'), 'procesando')
        donation.estado = nuevo_estado
        donation.referencia_pasarela = transaction_data.get('id')
        donation.wompi_response = transaction_data
        donation.save()

        logger.info(f"Donación {referencia} actualizada a {nuevo_estado}")

    # Certificado FUERA de la transacción: no se mantiene el bloqueo de fila
    # durante SMTP/PDF y sus errores no rompen el registro del pago.
    if nuevo_estado == 'completado' and not donation.certificado_enviado:
        try:
            pdf_bytes = generate_donation_certificate(
                nombre=donation.donante_nombre,
                documento=donation.donante_documento_cifrado,
                monto=donation.monto,
                referencia=donation.referencia,
                tipo=donation.tipo,
                fecha=donation.creado_en,
            )
            send_donation_email(donation, pdf_bytes)
            donation.certificado_enviado = True
            donation.save(update_fields=['certificado_enviado'])
        except Exception as ex:
            logger.error(
                f"Error enviando certificado para donación {referencia}: {ex}",
                exc_info=True,
            )

    return donation


class DonationViewSet(viewsets.GenericViewSet):
    """
    ViewSet para donaciones.

    Seguridad:
    - permission_classes = [AllowAny] a nivel de clase: las donaciones son
      públicas (cualquiera puede donar). El endpoint de estado también es
      público porque se consulta con la referencia (secreto por URL).
    - El webhook es público (lo llama Wompi sin sesión).
    - El throttle scope 'donate' aplica solo al action `initiate`.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]
    # Throttle scope usado por ScopedRateThrottle en el action `initiate`.
    throttle_scope = 'donate'
    lookup_field = 'referencia'

    def get_client_ip(self, request):
        """
        Obtiene la IP real del cliente.

        Seguridad: X-Forwarded-For puede contener una lista
        `client, proxy1, proxy2`. Tomamos el ÚLTIMO valor (no el primero) bajo
        el supuesto de que el proxy inverso confiable más cercano a Django
        (p.ej. Nginx) es quien APENDIZA la IP del cliente que lo contactó al
        final de la cadena. El primer valor, en cambio, podría estar
        controlado por el cliente (spoofing) si un proxy intermedio no validó
        la cabecera.
        SUPONE: se ejecuta detrás de un proxy confiable que reescribe / valida
        X-Forwarded-For. Si no hay proxy, se usa REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Última IP de la cadena, sin espacios.
            return x_forwarded_for.split(',')[-1].strip()
        return request.META.get('REMOTE_ADDR')

    @action(
        detail=False,
        methods=['post'],
        # Seguridad: las donaciones son públicas; throttle para limitar abuso.
        permission_classes=[AllowAny],
        throttle_classes=[ScopedRateThrottle],
    )
    def initiate(self, request):
        """Inicia el proceso de pago y retorna la info para el widget de Wompi"""
        serializer = InitiateDonationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        data = serializer.validated_data

        if not data.get('autorizacion_datos'):
            return Response({"error": "Debe aceptar el tratamiento de datos."}, status=status.HTTP_400_BAD_REQUEST)

        # Generar referencia (tipo-UUID)
        prefijo = data.get('tipo', 'donacion')[:4].upper()
        referencia = f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"

        # --- Sanitización del nombre del donante ----------------------------
        # Elimina espacios excesivos y caracteres de control.
        donante_nombre = ' '.join(data.get('donante_nombre', '').split())

        # --- Validación de beneficiario -------------------------------------
        # Se verifica que el beneficiario exista antes de crear la donación
        # para evitar registros huérfanos u orquestar datos inválidos.
        beneficiario_id = data.get('beneficiario_id')
        if beneficiario_id:
            from beneficiaries.models import Beneficiary  # Importación tardía
            if not Beneficiary.objects.filter(id=beneficiario_id).exists():
                return Response(
                    {"error": "El beneficiario especificado no existe."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Seguridad: atomicidad — si la creación de la sesión de Wompi falla,
        # se revierte la creación de la donación para evitar registros huérfanos
        # en estado 'pendiente' que nunca tendrán pago asociado.
        try:
            with transaction.atomic():
                # Crear registro pendiente
                donation = Donation.objects.create(
                    referencia=referencia,
                    tipo=data.get('tipo'),
                    monto=data.get('monto'),
                    donante_nombre=donante_nombre,
                    donante_email=data.get('donante_email'),
                    donante_documento_cifrado=data.get('donante_documento'),
                    donante_telefono_cifrado=data.get('donante_telefono'),
                    metodo_pago=data.get('metodo_pago'),
                    beneficiario_id=beneficiario_id,
                    autorizacion_datos=True,
                    ip_origen=self.get_client_ip(request)
                )

                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
                redirect_url = f"{frontend_url}?pago=exitoso&ref={referencia}"

                # Generar datos para Wompi (puede lanzar excepción si la API falla).
                payment_session = create_payment_session(
                    reference=referencia,
                    amount_cop=float(donation.monto),
                    description=f"Donación {donation.tipo} - Funcrees",
                    customer_email=donation.donante_email,
                    redirect_url=redirect_url
                )
        except Exception as e:
            # transaction.atomic() ya revirtió la creación de la donación.
            # Se registra el tipo de excepción explícitamente para facilitar
            # la depuración y el monitoreo de errores recurrentes.
            logger.error(
                f"Error iniciando donación {referencia}: "
                f"{type(e).__name__}: {e}",
                exc_info=True,
            )
            return Response(
                {"error": "No se pudo iniciar la donación. Intente nuevamente."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({
            "success": True,
            "referencia": referencia,
            "paymentSession": payment_session
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def webhook(self, request):
        """Recibe notificaciones de Wompi sobre el estado del pago"""
        payload = request.data
        received_signature = payload.get('signature', {}).get('checksum')

        if not verify_webhook_signature(payload, received_signature):
            # Se registra la IP del remitente para facilitar la detección
            # de patrones de ataque y el bloqueo en el firewall si es necesario.
            client_ip = self.get_client_ip(request)
            logger.warning(
                "Webhook de Wompi con firma inválida. Posible ataque. "
                "IP del remitente: %s",
                client_ip,
            )
            return Response({"error": "Firma inválida"}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get('event')
        data = payload.get('data', {})

        if event == 'transaction.updated':
            transaction_data = data.get('transaction', {})
            referencia = transaction_data.get('reference')

            if referencia:
                try:
                    # procesar_transaccion_wompi() aplica el estado con bloqueo
                    # pesimista, idempotencia y envío de certificado.
                    procesar_transaccion_wompi(referencia, transaction_data)
                except Donation.DoesNotExist:
                    logger.warning(f"Webhook: Donación no encontrada para referencia {referencia}")

        # Siempre devolver 200 a Wompi para evitar reintentos innecesarios.
        return Response({"received": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def status(self, request, referencia=None):
        """Consulta el estado de una donación.

        Seguridad: público por diseño (la referencia actúa como secreto
        compartido y se envía por URL). No expone datos sensibles más allá
        de lo que el donante ya introdujo.
        """
        try:
            donation = self.get_object()
            serializer = self.get_serializer(donation)
            return Response({"success": True, "donacion": serializer.data})
        except Exception:
            return Response({"error": "Donación no encontrada"}, status=status.HTTP_404_NOT_FOUND)
