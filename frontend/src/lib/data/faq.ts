/**
 * Preguntas Frecuentes (FAQ) institucional de FUNCREES.
 *
 * Fuente única para:
 *  - la página /preguntas-frecuentes (acordeón accesible), y
 *  - el JSON-LD schema.org/FAQPage que mejora el SEO del sitio.
 *
 * Cada ítem: id estable (ancla #), pregunta y respuesta. Las respuestas
 * son texto plano con URLs relativas entre corchetes dobles cuando
 * conviene enlazar ([[/donaciones]] → link interno); la página las
 * convierte en <a> sin tocar HTML crudo (sin riesgo XSS).
 */

export interface FaqItem {
	id: string;
	pregunta: string;
	respuesta: string;
}

export const FAQ_ITEMS: FaqItem[] = [
	{
		id: 'como-donar',
		pregunta: '¿Cómo puedo hacer una donación?',
		respuesta:
			'Puedes donar en línea desde nuestra página de donaciones con PSE (todos los bancos), tarjetas de crédito, Nequi o Daviplata a través de Wompi, nuestra pasarela de pago certificada. También puedes apoyar con transferencia o en nuestros eventos. [[/donaciones]]'
	},
	{
		id: 'seguridad-pagos',
		pregunta: '¿Es seguro donar en línea? ¿Qué es Wompi?',
		respuesta:
			'Sí. Los pagos los procesa Wompi, una pasarela de pago colombiana certificada por la banca (PCI-DSS). FUNCREES nunca ve ni almacena los datos de tu tarjeta o cuenta: solo recibimos la confirmación del pago y tu nombre para el certificado.'
	},
	{
		id: 'certificado-donacion',
		pregunta: '¿Recibo un certificado o comprobante de mi donación?',
		respuesta:
			'Sí. Al confirmarse tu aporte te enviamos un correo con el comprobante, y las donaciones empresariales reciben certificado oficial de donación emitido por la fundación. Revisa tu carpeta de spam si no lo ves en unos minutos.'
	},
	{
		id: 'boletas-eventos',
		pregunta: 'Compré una boleta para un evento, ¿cómo la consulto?',
		respuesta:
			'Al confirmar tu compra recibes un código de verificación de 10 caracteres por WhatsApp o correo. Ingrésalo en nuestra página de consulta de boletas para ver el estado de tu pago. También puedes imprimir tu boleta con código QR para presentarla en la puerta. [[/boletas]]'
	},
	{
		id: 'que-es-apadrinamiento',
		pregunta: '¿Qué incluye apadrinar a un adulto mayor?',
		respuesta:
			'Tu aporte mensual financia alimentación balanceada, medicamentos, terapias y acompañamiento emocional. Recibes un reporte mensual de impacto con el bienestar de la persona que apadrinas. Conoce los niveles Semilla, Raíz y Legado en la página de donaciones. [[/donaciones]]'
	},
	{
		id: 'como-se-usa-dinero',
		pregunta: '¿Cómo sé que mi dinero llega a las comunidades?',
		respuesta:
			'Publicamos nuestros números en vivo (recaudo, beneficiarios y ciudades atendidas) y un informe anual de rendición de cuentas con los estados financieros de la fundación. La transparencia es parte de nuestro compromiso. [[/numeros]]'
	},
	{
		id: 'datos-personales',
		pregunta: '¿Qué hacen con mis datos personales?',
		respuesta:
			'Tratamos tus datos conforme a la Ley 1581 de 2012 (protección de datos de Colombia): solo los usamos para procesar tu donación, enviarte tu certificado y comunicaciones que tú autorices. Tu autorización es explícita y puedes solicitar actualizar o eliminar tus datos escribiéndonos. [[/privacidad]]'
	},
	{
		id: 'voluntariado',
		pregunta: '¿Cómo puedo ser voluntario?',
		respuesta:
			'¡Nos encantaría tenerte! Escríbenos por el formulario de contacto indicando tu ciudad, disponibilidad y en qué te gustaría ayudar (comedores, eventos, terapias, comunicación). El equipo te responde en horario hábil. [[/contacto]]'
	},
	{
		id: 'alianzas-empresas',
		pregunta: 'Mi empresa quiere apoyar, ¿qué opciones hay?',
		respuesta:
			'Tenemos alianzas de patrocinio con visibilidad en redes y eventos, apadrinamiento corporativo y voluntariados de empresa. Cuéntanos tu interés por el formulario y armamos una propuesta a la medida. [[/contacto]]'
	},
	{
		id: 'donde-operan',
		pregunta: '¿Dónde trabaja FUNCREES?',
		respuesta:
			'Nuestra sede está en Sincelejo, Sucre, y atendemos comunidades de todo el departamento y el territorio nacional mediante programas de comedores, salud y educación para adultos mayores y jóvenes.'
	}
];

/**
 * Convierte el marcado [[/ruta]] de una respuesta en un enlace interno.
 * Devuelve segmentos {texto, href|null} para renderizar sin innerHTML.
 */
export function parsearRespuesta(respuesta: string): Array<{ texto: string; href: string | null }> {
	const partes: Array<{ texto: string; href: string | null }> = [];
	const regex = /\[\[([^\]]+)\]\]/g;
	let ultimo = 0;
	let m: RegExpExecArray | null;
	while ((m = regex.exec(respuesta)) !== null) {
		if (m.index > ultimo) partes.push({ texto: respuesta.slice(ultimo, m.index), href: null });
		partes.push({ texto: 'aquí', href: m[1] });
		ultimo = m.index + m[0].length;
	}
	if (ultimo < respuesta.length) partes.push({ texto: respuesta.slice(ultimo), href: null });
	return partes.length > 0 ? partes : [{ texto: respuesta, href: null }];
}

/** JSON-LD schema.org/FAQPage para SEO (Google Rich Results). */
export function buildFaqJsonLd(items: FaqItem[] = FAQ_ITEMS): object {
	return {
		'@context': 'https://schema.org',
		'@type': 'FAQPage',
		mainEntity: items.map((it) => ({
			'@type': 'Question',
			name: it.pregunta,
			acceptedAnswer: { '@type': 'Answer', text: it.respuesta.replace(/\[\[[^\]]+\]\]/g, '').trim() }
		}))
	};
}
