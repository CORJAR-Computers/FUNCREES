<script lang="ts">
        import Seo from '$lib/components/Seo.svelte';
        import type { UiEventDetail } from '$lib/types';

        /**
         * Página pública de detalle de evento (/eventos/[id]):
         * - SSR desde GET /api/events/<id>/ con fallback amable si falla.
         * - JSON-LD schema.org/Event para resultados enriquecidos en Google.
         * - CTA que abre el checkout real en /eventos?evento=<id>.
         */

        interface Props {
                data: { evento: UiEventDetail | null; notFound: boolean; id: string };
        }

        const { data }: Props = $props();

        const evento = $derived(data.evento);

        const WHATSAPP = '573137924439';

        /** Precio parseado (0 = aporte libre / campaña sin costo). */
        const costoNumerico = $derived(Number(evento?.costoBono ?? 0) || 0);
        const esEventoConBono = $derived(costoNumerico > 0);

        /** Texto de fecha largo: "sábado 10 de octubre de 2026" (locale es-CO). */
        const fechaLarga = $derived.by(() => {
                if (!evento?.fechaISO) return null;
                const d = new Date(`${evento.fechaISO}T12:00:00`);
                if (Number.isNaN(d.getTime())) return null;
                return d.toLocaleDateString('es-CO', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                });
        });

        const horaLegible = $derived.by(() => {
                if (!evento?.horaISO) return null;
                const [hStr, mStr] = (evento.horaISO.split(':') ?? []) as [string, string?];
                const h = parseInt(hStr ?? '0', 10);
                if (Number.isNaN(h)) return evento.hora;
                const period = h >= 12 ? 'p.m.' : 'a.m.';
                const h12 = h % 12 === 0 ? 12 : h % 12;
                return `${h12}:${mStr ?? '00'} ${period}`;
        });

        /** Fecha ya pasada (para deshabilitar la compra de eventos vencidos). */
        const eventoPasado = $derived.by(() => {
                if (!evento?.dateObj) return false;
                return new Date(evento.dateObj).getTime() < Date.now();
        });

        const cuposRestantes = $derived.by(() => {
                if (!evento) return null;
                if (evento.cupoDisponible != null) return evento.cupoDisponible;
                if (evento.cupoMaximo != null) return evento.cupoMaximo;
                return null; // sin límite declarado
        });

        /** JSON-LD schema.org/Event (solo si hay fecha; campañas permanentes no califican). */
        const eventJsonLd = $derived.by(() => {
                if (!evento) return undefined;
                const ld: Record<string, unknown> = {
                        '@context': 'https://schema.org',
                        '@type': 'Event',
                        name: evento.titulo,
                        description: evento.desc || 'Evento solidario de Fundación Funcrees Colombia.',
                        eventStatus: 'https://schema.org/EventScheduled',
                        organizer: {
                                '@type': 'NGO',
                                name: 'Fundación Crece Una Esperanza Social (FUNCREES) Colombia',
                                url: 'https://funcreescolombia.org'
                        }
                };
                if (evento.fechaISO) {
                        ld.startDate = evento.horaISO
                                ? `${evento.fechaISO}T${evento.horaISO}`
                                : evento.fechaISO;
                }
                if (evento.dateObj) ld.endDate = evento.dateObj;
                ld.location = {
                        '@type': 'Place',
                        name: evento.lugar,
                        address: {
                                '@type': 'PostalAddress',
                                addressLocality: 'Sincelejo',
                                addressRegion: 'Sucre',
                                addressCountry: 'CO'
                        }
                };
                if (evento.imagen) ld.image = [evento.imagen];
                ld.offers = {
                        '@type': 'Offer',
                        price: costoNumerico,
                        priceCurrency: 'COP',
                        availability: cuposRestantes === 0
                                ? 'https://schema.org/SoldOut'
                                : 'https://schema.org/InStock',
                        url: `https://funcreescolombia.org/eventos/${evento.id}`
                };
                return ld;
        });

        /** Mensaje prellenado de WhatsApp para campañas de aporte libre. */
        function abrirWhatsAppCampania(): void {
                if (!evento) return;
                const msg = encodeURIComponent(
                        `Hola Fundación FUNCREESCOLOMBIA, deseo apoyar la campaña "${evento.titulo}".`
                );
                window.open(`https://wa.me/${WHATSAPP}?text=${msg}`, '_blank');
        }

        function fmtCOP(n: number): string {
                return '$' + String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        }

        /** Enlace "Añadir a Google Calendar" (template URL oficial, sin dependencias).
         *  Duración supuesta de 2h para eventos con hora; campañas sin fecha no lo muestran. */
        const googleCalendarUrl = $derived.by(() => {
                if (!evento?.fechaISO) return null;
                const compact = (d: Date): string =>
                        `${d.getUTCFullYear()}${String(d.getUTCMonth() + 1).padStart(2, '0')}${String(d.getUTCDate()).padStart(2, '0')}T${String(d.getUTCHours()).padStart(2, '0')}${String(d.getUTCMinutes()).padStart(2, '0')}00Z`;

                let start: Date;
                let end: Date;
                if (evento.horaISO) {
                        start = new Date(`${evento.fechaISO}T${evento.horaISO}`);
                        end = new Date(start.getTime() + 2 * 60 * 60 * 1000);
                } else {
                        // Evento de todo el día: bloque de un día (end exclusivo)
                        start = new Date(`${evento.fechaISO}T00:00:00`);
                        end = new Date(start.getTime() + 24 * 60 * 60 * 1000);
                }
                if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return null;

                const params = new URLSearchParams({
                        action: 'TEMPLATE',
                        text: `${evento.titulo} — FUNCREES Colombia`,
                        dates: `${compact(start)}/${compact(end)}`,
                        location: evento.lugar,
                        details:
                                evento.desc ||
                                'Evento solidario de Fundación Funcrees Colombia. ¡Tu apoyo dignifica la vida de nuestros abuelitos!'
                });
                return `https://calendar.google.com/calendar/render?${params.toString()}`;
        });

        /** Compartir el evento con Web Share API y fallback a copiar enlace. */
        let compartidoOk = $state(false);

        async function compartirEvento(): Promise<void> {
                if (!evento) return;
                const url = `${window.location.origin}/eventos/${evento.id}`;
                const data: ShareData = {
                        title: evento.titulo,
                        text: `Conoce ${evento.titulo} y apoya a nuestros abuelitos —`,
                        url
                };
                if (navigator.share) {
                        try {
                                await navigator.share(data);
                        } catch {
                                /* usuario canceló — no es error */
                        }
                        return;
                }
                // Fallback: copiar al portapapeles
                try {
                        await navigator.clipboard.writeText(url);
                        compartidoOk = true;
                        setTimeout(() => (compartidoOk = false), 2000);
                } catch {
                        window.open(`https://wa.me/?text=${encodeURIComponent(`${data.text} ${url}`)}`, '_blank');
                }
        }
</script>

<Seo
        title={evento ? `${evento.titulo} | Eventos FUNCREES` : 'Evento no encontrado | FUNCREES'}
        description={evento
                ? (evento.desc || `${evento.titulo} — evento solidario de Fundación Funcrees Colombia en ${evento.lugar}.`).slice(0, 160)
                : 'El evento que buscas no está disponible. Conoce los eventos y campañas vigentes de Fundación Funcrees Colombia.'}
        path={evento ? `/eventos/${evento.id}` : '/eventos'}
        jsonLd={eventJsonLd}
        image={evento?.imagen || undefined}
        imageAlt={evento ? `${evento.titulo} — Fundación Funcrees Colombia` : undefined}
        ogType="article"
/>

<section class="detalle-view">
        <div class="detalle-container">
                <nav class="detalle-breadcrumb" aria-label="Miga de pan">
                        <a href="/eventos"><i class="fa-solid fa-arrow-left"></i> Todos los eventos</a>
                </nav>

                {#if evento}
                                <article class="detalle-card">
                                                {#if evento.imagen}
                                                                <div class="detalle-hero">
                                                                                <picture>
                                                                                                {#if evento.imagen_webp_srcset}
                                                                                                                <source
                                                                                                                                srcset={evento.imagen_webp_srcset}
                                                                                                                                sizes="(max-width: 768px) 100vw, 820px"
                                                                                                                                type="image/webp"
                                                                                                                />
                                                                                                {/if}
                                                                                                <img
                                                                                                                src={evento.imagen}
                                                                                                                alt="{evento.titulo} — Fundación FUNCREES"
                                                                                                                fetchpriority="high"
                                                                                                />
                                                                                </picture>
                                                                                <span class="detalle-categoria" class:es-campania={evento.category === 'campania'}>
                                                                                                {evento.category === 'campania' ? 'Campaña' : 'Evento'}
                                                                                </span>
                                                                </div>
                                                {:else}
                                                                <div class="detalle-hero detalle-hero-placeholder">
                                                                                <i class="fa-solid fa-calendar-days" aria-hidden="true"></i>
                                                                                <span class="detalle-categoria" class:es-campania={evento.category === 'campania'}>
                                                                                                {evento.category === 'campania' ? 'Campaña' : 'Evento'}
                                                                                </span>
                                                                </div>
                                                {/if}

                                                <div class="detalle-body">
                                                                <h1 class="detalle-titulo">{evento.titulo}</h1>
                                                                {#if evento.desc}
                                                                                <p class="detalle-desc">{evento.desc}</p>
                                                                {/if}

                                                                <ul class="detalle-facts" aria-label="Datos del evento">
                                                                                <li>
                                                                                                <i class="fa-solid fa-calendar-day"></i>
                                                                                                <div>
                                                                                                                <span class="fact-label">Fecha</span>
                                                                                                                <span class="fact-value">{fechaLarga ?? evento.fecha}</span>
                                                                                                </div>
                                                                                </li>
                                                                                <li>
                                                                                                <i class="fa-solid fa-clock"></i>
                                                                                                <div>
                                                                                                                <span class="fact-label">Hora</span>
                                                                                                                <span class="fact-value">{horaLegible ?? evento.hora}</span>
                                                                                                </div>
                                                                                </li>
                                                                                <li>
                                                                                                <i class="fa-solid fa-location-dot"></i>
                                                                                                <div>
                                                                                                                <span class="fact-label">Lugar</span>
                                                                                                                <span class="fact-value">{evento.lugar}</span>
                                                                                                </div>
                                                                                </li>
                                                                                {#if cuposRestantes !== null}
                                                                                                <li>
                                                                                                                <i class="fa-solid fa-users"></i>
                                                                                                                <div>
                                                                                                                                <span class="fact-label">Cupos</span>
                                                                                                                                <span class="fact-value">
                                                                                                                                                {cuposRestantes > 0 ? `${cuposRestantes} disponibles` : 'Agotados'}
                                                                                                                                </span>
                                                                                                                </div>
                                                                                                </li>
                                                                                {/if}
                                                                </ul>

                                                                <div class="detalle-cta-row">
                                                                                <div class="detalle-precio">
                                                                                                <span class="precio-label">
                                                                                                                {esEventoConBono ? 'Precio del bono' : 'Aporte'}
                                                                                                </span>
                                                                                                <span class="precio-value">
                                                                                                                {esEventoConBono ? `${fmtCOP(costoNumerico)} COP` : 'Libre'}
                                                                                                </span>
                                                                                </div>

                                                                                {#if eventoPasado}
                                                                                                <span class="detalle-finalizado">
                                                                                                                <i class="fa-solid fa-hourglass-end"></i> Evento finalizado
                                                                                                </span>
                                                                                {:else if esEventoConBono}
                                                                                                <a
                                                                                                                class="btn detalle-btn"
                                                                                                                href="/eventos?evento={evento.id}"
                                                                                                >
                                                                                                                <i class="fa-solid fa-ticket"></i> Adquirir Bono
                                                                                                </a>
                                                                                {:else}
                                                                                                <button class="btn detalle-btn" onclick={abrirWhatsAppCampania}>
                                                                                                                <i class="fa-brands fa-whatsapp"></i> Quiero Apoyar
                                                                                                </button>
                                                                                {/if}
                                                                </div>

                                                                <div class="detalle-extra">
                                                                {#if googleCalendarUrl}
                                                                        <a
                                                                                class="detalle-accion"
                                                                                href={googleCalendarUrl}
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                        >
                                                                                <i class="fa-regular fa-calendar-plus"></i> Añadir a Google Calendar
                                                                        </a>
                                                                {/if}
                                                                <a class="detalle-accion" href="/calendario.ics" download="calendario-funcrees.ics" title="Agrega todos nuestros eventos a tu calendario">
                                                                        <i class="fa-solid fa-calendar-days"></i> Ver todos en mi calendario
                                                                </a>
                                                                <button type="button" class="detalle-accion" onclick={compartirEvento}>
                                                                        <i class="fa-solid fa-share-nodes"></i>
                                                                        {compartidoOk ? '¡Enlace copiado!' : 'Compartir evento'}
                                                                </button>
                                                                <a
                                                                        class="detalle-accion detalle-accion-consulta"
                                                                        href="/contacto?tipo=eventos&asunto={encodeURIComponent(evento.titulo)}"
                                                                >
                                                                        <i class="fa-regular fa-circle-question"></i> ¿Dudas? Escríbenos
                                                                </a>
                                                        </div>

                                                        <p class="detalle-nota">
                                                                                <i class="fa-solid fa-circle-info"></i>
                                                                                <span>
                                                                                                El pago se completa en la lista de eventos. Después de tu compra recibirás
                                                                                                un <strong>código de verificación</strong> — consúltalo en
                                                                                                <a href="/boletas">Consulta tu Boleta</a>.
                                                                                </span>
                                                                </p>
                                                </div>
                                </article>
                {:else if data.notFound}
                                <div class="detalle-vacio" role="status">
                                                <i class="fa-solid fa-calendar-xmark"></i>
                                                <h1>Evento no encontrado</h1>
                                                <p>
                                                        El evento <code>{data.id}</code> no existe o ya no está publicado.
                                                        Quizá terminó o fue archivado por la fundación.
                                                </p>
                                                <a class="btn detalle-btn" href="/eventos">Ver eventos vigentes</a>
                                </div>
                {:else}
                                <div class="detalle-vacio" role="status">
                                                <i class="fa-solid fa-plug-circle-xmark"></i>
                                                <h1>No pudimos cargar este evento</h1>
                                                <p>
                                                        Hay un problema de conexión con el servidor. Intenta de nuevo en unos
                                                        momentos o escríbenos por WhatsApp al
                                                        <a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener noreferrer">+57 313 792 4439</a>.
                                                </p>
                                                <a class="btn detalle-btn" href="/eventos">Ver eventos vigentes</a>
                                </div>
                {/if}
        </div>
</section>

<style>
                .detalle-view {
                                min-height: 100vh;
                                padding: 2rem 1rem 4rem;
                                background: var(--bg-secondary);
                }

                .detalle-container {
                                max-width: 860px;
                                margin: 0 auto;
                }

                /* Breadcrumb */
                .detalle-breadcrumb {
                                margin-bottom: 1.2rem;
                }

                .detalle-breadcrumb a {
                                display: inline-flex;
                                align-items: center;
                                gap: 0.5rem;
                                color: var(--text-muted);
                                text-decoration: none;
                                font-weight: 600;
                                font-size: 0.92rem;
                                padding: 0.5rem 0.9rem;
                                border-radius: 999px;
                                border: 1px solid var(--border-color);
                                background: var(--bg-card);
                                transition:
                                                color 0.2s ease,
                                                border-color 0.2s ease,
                                                transform 0.2s ease;
                }

                .detalle-breadcrumb a:hover,
                .detalle-breadcrumb a:focus-visible {
                                color: var(--primary);
                                border-color: var(--primary);
                                transform: translateX(-2px);
                }

                /* Tarjeta principal */
                .detalle-card {
                                background: var(--bg-card);
                                border: 1px solid var(--border-color);
                                border-radius: var(--radius-lg, 20px);
                                overflow: hidden;
                                box-shadow: var(--shadow-md);
                                animation: detalle-aparecer 0.4s ease both;
                }

                @keyframes detalle-aparecer {
                                from {
                                                opacity: 0;
                                                transform: translateY(10px);
                                }
                                to {
                                                opacity: 1;
                                                transform: translateY(0);
                                }
                }

                /* Hero con imagen */
                .detalle-hero {
                                position: relative;
                                max-height: 360px;
                                overflow: hidden;
                                background: var(--primary-soft);
                }

                .detalle-hero img {
                                width: 100%;
                                height: 100%;
                                max-height: 360px;
                                object-fit: cover;
                                display: block;
                }

                .detalle-hero::after {
                                content: '';
                                position: absolute;
                                inset: 0;
                                background: linear-gradient(180deg, rgba(0, 0, 0, 0) 55%, rgba(0, 0, 0, 0.35));
                                pointer-events: none;
                }

                .detalle-hero-placeholder {
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                height: 200px;
                }

                .detalle-hero-placeholder i {
                                font-size: 4rem;
                                color: var(--primary);
                                opacity: 0.35;
                }

                .detalle-categoria {
                                position: absolute;
                                top: 1rem;
                                left: 1rem;
                                z-index: 1;
                                padding: 0.4rem 1rem;
                                border-radius: 999px;
                                background: var(--primary);
                                color: #fff;
                                font-size: 0.78rem;
                                font-weight: 700;
                                letter-spacing: 0.08em;
                                text-transform: uppercase;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
                }

                .detalle-categoria.es-campania {
                                background: #b45309;
                }

                /* Cuerpo */
                .detalle-body {
                                padding: 1.75rem;
                }

                .detalle-titulo {
                                margin: 0 0 0.75rem;
                                font-size: clamp(1.5rem, 4vw, 2.1rem);
                                line-height: 1.2;
                                color: var(--text-main);
                }

                .detalle-desc {
                                color: var(--text-muted);
                                line-height: 1.7;
                                margin: 0 0 1.5rem;
                                font-size: 1.02rem;
                }

                /* Facts en grilla responsiva */
                .detalle-facts {
                                list-style: none;
                                margin: 0 0 1.75rem;
                                padding: 0;
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 0.85rem;
                }

                .detalle-facts li {
                                display: flex;
                                align-items: center;
                                gap: 0.85rem;
                                padding: 0.85rem 1rem;
                                background: var(--primary-soft);
                                border: 1px solid var(--border-color);
                                border-radius: 12px;
                                transition:
                                                transform 0.25s ease,
                                                border-color 0.25s ease,
                                                box-shadow 0.25s ease;
                }

                /* Micro-interacción: cada dato "vive" al pasar el cursor */
                .detalle-facts li:hover {
                                transform: translateY(-3px);
                                border-color: var(--primary);
                                box-shadow: 0 6px 18px -8px var(--primary-trans, rgba(0, 0, 0, 0.25));
                }

                .detalle-facts li:hover i {
                                transform: scale(1.12);
                }

                .detalle-facts i {
                                color: var(--primary);
                                font-size: 1.15rem;
                                width: 1.4rem;
                                text-align: center;
                                transition: transform 0.25s ease;
                }

                @media (prefers-reduced-motion: reduce) {
                                .detalle-facts li,
                                .detalle-facts i {
                                                transition: none;
                                }
                                .detalle-facts li:hover {
                                                transform: none;
                                }
                                .detalle-facts li:hover i {
                                                transform: none;
                                }
                }

                .fact-label {
                                display: block;
                                font-size: 0.72rem;
                                text-transform: uppercase;
                                letter-spacing: 0.08em;
                                color: var(--text-muted);
                                font-weight: 700;
                }

                .fact-value {
                                display: block;
                                color: var(--text-main);
                                font-weight: 600;
                                font-size: 0.95rem;
                                text-transform: none;
                }

                /* Fila CTA: precio + botón */
                .detalle-cta-row {
                                display: flex;
                                align-items: center;
                                justify-content: space-between;
                                gap: 1.25rem;
                                flex-wrap: wrap;
                                padding: 1.25rem;
                                border: 2px dashed var(--primary-trans, var(--border-color));
                                border-radius: 14px;
                                margin-bottom: 1rem;
                }

                .precio-label {
                                display: block;
                                font-size: 0.75rem;
                                text-transform: uppercase;
                                letter-spacing: 0.08em;
                                color: var(--text-muted);
                                font-weight: 700;
                }

                .precio-value {
                                display: block;
                                font-size: 1.7rem;
                                font-weight: 800;
                                color: var(--primary-dark, var(--primary));
                                line-height: 1.15;
                }

                .detalle-btn {
                                display: inline-flex;
                                align-items: center;
                                gap: 0.6rem;
                                padding: 0.9rem 1.7rem;
                                min-height: 48px;
                                font-size: 1rem;
                                background: var(--primary);
                                color: #fff;
                                border-radius: 12px;
                                text-decoration: none;
                                border: none;
                                cursor: pointer;
                                font-weight: 700;
                                transition:
                                                transform 0.2s ease,
                                                box-shadow 0.2s ease,
                                                background 0.2s ease;
                }

                .detalle-btn:hover,
                .detalle-btn:focus-visible {
                                transform: translateY(-2px);
                                box-shadow: 0 8px 20px var(--primary-trans, rgba(0, 0, 0, 0.15));
                                background: var(--primary-dark, var(--primary));
                }

                .detalle-finalizado {
                                display: inline-flex;
                                align-items: center;
                                gap: 0.5rem;
                                padding: 0.7rem 1.2rem;
                                border-radius: 12px;
                                background: var(--primary-soft);
                                color: var(--text-muted);
                                font-weight: 700;
                                border: 1px solid var(--border-color);
                }

                /* Acciones secundarias: calendario, compartir, consultas */
                .detalle-extra {
                        display: flex;
                        gap: 0.65rem;
                        flex-wrap: wrap;
                        margin-bottom: 1.1rem;
                }

                .detalle-accion {
                        display: inline-flex;
                        align-items: center;
                        gap: 0.5rem;
                        padding: 0.55rem 1rem;
                        min-height: 44px;
                        border-radius: 10px;
                        border: 1px solid var(--border-color);
                        background: var(--bg-card);
                        color: var(--text-main);
                        font-size: 0.88rem;
                        font-weight: 600;
                        text-decoration: none;
                        cursor: pointer;
                        transition:
                                border-color 0.2s ease,
                                color 0.2s ease,
                                transform 0.2s ease,
                                background 0.2s ease;
                }

                .detalle-accion i {
                        color: var(--primary);
                }

                .detalle-accion:hover,
                .detalle-accion:focus-visible {
                        border-color: var(--primary);
                        color: var(--primary);
                        transform: translateY(-2px);
                }

                .detalle-accion-consulta {
                        border-style: dashed;
                }

                .detalle-nota {
                                display: flex;
                                gap: 0.55rem;
                                align-items: flex-start;
                                margin: 0;
                                font-size: 0.86rem;
                                color: var(--text-muted);
                                line-height: 1.6;
                }

                .detalle-nota i {
                                margin-top: 0.2rem;
                                color: var(--primary);
                }

                .detalle-nota a {
                                color: var(--primary);
                                font-weight: 600;
                }

                /* Estados vacío / error */
                .detalle-vacio {
                                text-align: center;
                                background: var(--bg-card);
                                border: 1px solid var(--border-color);
                                border-radius: var(--radius-lg, 20px);
                                padding: 3.5rem 1.5rem;
                                box-shadow: var(--shadow-md);
                }

                .detalle-vacio i {
                                font-size: 3.2rem;
                                color: var(--primary);
                                opacity: 0.4;
                }

                .detalle-vacio h1 {
                                margin: 1rem 0 0.5rem;
                                color: var(--text-main);
                }

                .detalle-vacio p {
                                color: var(--text-muted);
                                max-width: 460px;
                                margin: 0 auto 1.5rem;
                                line-height: 1.65;
                }

                .detalle-vacio code {
                                background: var(--primary-soft);
                                border: 1px solid var(--border-color);
                                border-radius: 6px;
                                padding: 0.1rem 0.45rem;
                                font-weight: 700;
                }

                /* Respeto a reduce-motion (WCAG 2.1) */
                @media (prefers-reduced-motion: reduce) {
                                .detalle-card,
                                .detalle-breadcrumb a,
                                .detalle-btn {
                                                animation: none;
                                                transition: none;
                                }
                }

                @media (max-width: 560px) {
                                .detalle-body {
                                                padding: 1.25rem;
                                }

                                .detalle-cta-row {
                                                flex-direction: column;
                                                align-items: stretch;
                                                text-align: center;
                                }

                                .detalle-btn {
                                                justify-content: center;
                                }
                }
</style>
