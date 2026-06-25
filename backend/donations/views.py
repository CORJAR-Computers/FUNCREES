import uuid
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Donation
from .serializers import DonationSerializer, InitiateDonationSerializer
from .services.wompi import create_payment_session, verify_webhook_signature

logger = logging.getLogger(__name__)

class DonationViewSet(viewsets.GenericViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'referencia'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    @action(detail=False, methods=['post'])
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

        # Crear registro pendiente
        donation = Donation.objects.create(
            referencia=referencia,
            tipo=data.get('tipo'),
            monto=data.get('monto'),
            donante_nombre=data.get('donante_nombre'),
            donante_email=data.get('donante_email'),
            donante_documento_cifrado=data.get('donante_documento'),
            donante_telefono_cifrado=data.get('donante_telefono'),
            metodo_pago=data.get('metodo_pago'),
            beneficiario_id=data.get('beneficiario_id'),
            autorizacion_datos=True,
            ip_origen=self.get_client_ip(request)
        )

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
        redirect_url = f"{frontend_url}?pago=exitoso&ref={referencia}"

        # Generar datos para Wompi
        payment_session = create_payment_session(
            reference=referencia,
            amount_cop=float(donation.monto),
            description=f"Donación {donation.tipo} - Funcrees",
            customer_email=donation.donante_email,
            redirect_url=redirect_url
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
            logger.warning("Webhook de Wompi con firma inválida. Posible ataque.")
            return Response({"error": "Firma inválida"}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get('event')
        data = payload.get('data', {})

        if event == 'transaction.updated':
            transaction = data.get('transaction', {})
            referencia = transaction.get('reference')
            estado_wompi = transaction.get('status')

            if referencia:
                try:
                    donation = Donation.objects.get(referencia=referencia)
                    
                    estado_map = {
                        'APPROVED': 'completado',
                        'DECLINED': 'fallido',
                        'VOIDED': 'reembolsado',
                        'ERROR': 'fallido'
                    }
                    nuevo_estado = estado_map.get(estado_wompi, 'procesando')
                    
                    donation.estado = nuevo_estado
                    donation.referencia_pasarela = transaction.get('id')
                    donation.wompi_response = transaction
                    donation.save()
                    
                    logger.info(f"Webhook: Donación {referencia} actualizada a {nuevo_estado}")
                    
                    # TODO: Si es completado y no se ha enviado el certificado, enviar email
                    # if nuevo_estado == 'completado' and not donation.certificado_enviado:
                    #     enviar_certificado(donation)

                except Donation.DoesNotExist:
                    logger.warning(f"Webhook: Donación no encontrada para referencia {referencia}")

        # Siempre devolver 200 a Wompi
        return Response({"received": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def status(self, request, referencia=None):
        """Consulta el estado de una donación"""
        try:
            donation = self.get_object()
            serializer = self.get_serializer(donation)
            return Response({"success": True, "donacion": serializer.data})
        except Exception:
            return Response({"error": "Donación no encontrada"}, status=status.HTTP_404_NOT_FOUND)
