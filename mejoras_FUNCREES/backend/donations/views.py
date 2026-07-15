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
from .services.wompi import create_payment_session, verify_webhook_signature
from .services.pdf_generator import generate_donation_certificate
from .services.email_service import send_donation_email

logger = logging.getLogger(__name__)


class DonationViewSet(viewsets.GenericViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'donate'
    lookup_field = 'referencia'

    def get_client_ip(self, request):
        """Extrae la IP real del cliente, considerando proxies inversos."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[-1].strip()
        return request.META.get('REMOTE_ADDR')

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        throttle_classes=[ScopedRateThrottle],
    )
    def initiate(self, request):
        """Inicia una nueva donación y crea la sesión de pago en Wompi."""
        serializer = InitiateDonationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        data = serializer.validated_data

        if not data.get('autorizacion_datos'):
            return Response({"error": "Debe aceptar el tratamiento de datos."}, status=status.HTTP_400_BAD_REQUEST)

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

        prefijo = data.get('tipo', 'donacion')[:4].upper()
        referencia = f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"

        try:
            with transaction.atomic():
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

                payment_session = create_payment_session(
                    reference=referencia,
                    amount_cop=float(donation.monto),
                    description=f"Donación {donation.tipo} - Funcrees",
                    customer_email=donation.donante_email,
                    redirect_url=redirect_url
                )
        except Exception as e:
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
        """Recibe notificaciones de Wompi sobre cambios de estado de transacciones."""
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
            estado_wompi = transaction_data.get('status')

            if referencia:
                try:
                    with transaction.atomic():
                        donation = Donation.objects.select_for_update().get(referencia=referencia)

                        if donation.estado == 'completado':
                            logger.info(
                                f"Webhook idempotente: donación {referencia} ya "
                                f"completada, se omite reproceso."
                            )
                            return Response({"received": True}, status=status.HTTP_200_OK)

                        estado_map = {
                            'APPROVED': 'completado',
                            'DECLINED': 'fallido',
                            'VOIDED': 'reembolsado',
                            'ERROR': 'fallido'
                        }
                        nuevo_estado = estado_map.get(estado_wompi, 'procesando')

                        donation.estado = nuevo_estado
                        donation.referencia_pasarela = transaction_data.get('id')
                        donation.wompi_response = transaction_data
                        donation.save()

                        logger.info(f"Webhook: Donación {referencia} actualizada a {nuevo_estado}")

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
                                    f"Error enviando certificado para donación "
                                    f"{referencia}: {ex}",
                                    exc_info=True
                                )

                except Donation.DoesNotExist:
                    logger.warning(f"Webhook: Donación no encontrada para referencia {referencia}")

        return Response({"received": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def status(self, request, referencia=None):
        """
        Consulta el estado de una donación por su referencia.

        MODELO DE SEGURIDAD:
        La referencia UUID funciona como un secreto compartido: solo se
        entrega al donante después de iniciar la donación y no es predecible
        (UUID v4 truncado + prefijo).  Esto es aceptable para una fundación
        sin autenticación de usuarios, pero implica que cualquiera que
        conozca la referencia puede consultar el estado.  Si en el futuro
        se requiere acceso restringido, se deberá añadir autenticación
        (ej: token temporal enviado por correo).
        """
        try:
            donation = self.get_object()
            serializer = self.get_serializer(donation)
            return Response({"success": True, "donacion": serializer.data})
        except Exception:
            return Response({"error": "Donación no encontrada"}, status=status.HTTP_404_NOT_FOUND)