<script lang="ts">
        import { toast } from '$lib/stores/toast.svelte';
        import Seo from '$lib/components/Seo.svelte';

        function onActionClick(action: string): void {
                toast.show(`Acción seleccionada: ${action}`, 'success');
        }
</script>

<Seo
        title="Fundación Funcrees Colombia | Crece Una Esperanza"
        description="Fundación Funcrees Colombia en Sincelejo. Soluciones sociales innovadoras para un impacto positivo, dignificación y atención integral al adulto mayor en Sucre."
        path="/"
/>

<svelte:head>
        <!-- Preload del LCP: antes era un PNG de 2.6 MB vía CSS background-image
             (sin preload, sin srcset). Ahora: WebP responsivo precargado. -->
        <link
                rel="preload"
                as="image"
                imagesrcset="/assets/hero-fundacion-480.webp 480w, /assets/hero-fundacion-960.webp 960w, /assets/hero-fundacion-1920.webp 1920w"
                imagesizes="100vw"
                fetchpriority="high"
        />
</svelte:head>

<section id="inicio" class="view-section active">
        <div class="hero">
                <div class="hero-bg-leaves">
                        <svg class="leaf-svg leaf-1" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M17 2 C15 5 11 8 8 11 C5 14 3 17 2 22 C7 21 10 19 13 16 C16 13 19 9 22 7 C21 5 19 3 17 2 Z" fill="#578c57" />
                        </svg>
                        <svg class="leaf-svg leaf-2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M17 2 C15 5 11 8 8 11 C5 14 3 17 2 22 C7 21 10 19 13 16 C16 13 19 9 22 7 C21 5 19 3 17 2 Z" fill="#419572" />
                        </svg>
                        <svg class="leaf-svg leaf-3" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M17 2 C15 5 11 8 8 11 C5 14 3 17 2 22 C7 21 10 19 13 16 C16 13 19 9 22 7 C21 5 19 3 17 2 Z" fill="#2d502d" />
                        </svg>
                </div>

                <!-- LCP: <img> responsivo WebP (2.6 MB PNG → 21-190 KB según viewport) -->
                <img
                        class="hero-bg-img"
                        src="/assets/hero-fundacion-1920.webp"
                        srcset="/assets/hero-fundacion-480.webp 480w, /assets/hero-fundacion-960.webp 960w, /assets/hero-fundacion-1920.webp 1920w"
                        sizes="100vw"
                        alt="Comunidad de la Fundación FUNCREES en Sincelejo, Sucre"
                        loading="eager"
                        fetchpriority="high"
                        decoding="async"
                />
                <div class="hero-overlay" aria-hidden="true"></div>

                <div class="hero-container">
                        <div class="hero-content">
                                <span class="hero-tag">
                                        <i class="fa-solid fa-seedling"></i> Sincelejo, Sucre
                                </span>
                                <h1 class="hero-title">Soluciones Sociales Innovadoras para un Impacto Positivo y Duradero</h1>
                                <p class="hero-desc">
                                        Apoyamos a nuestros abuelitos a través de la inclusión integral, salud preventiva comunitaria y modelos autosostenibles.
                                </p>
                                <div class="hero-actions">
                                        <a href="/quienes-somos" class="btn btn-primary">Conoce Nuestra Labor</a>
                                        <a href="/contacto" class="btn btn-outline">Únete como Aliado</a>
                                </div>
                        </div>

                        <div class="hero-card-featured">
                                <h3 class="hero-card-title">Adultos Mayores Atendidos</h3>
                                <span class="hero-card-stat">+120</span>
                                <p class="hero-card-desc">
                                        Reciben atención nutricional, médica preventiva, talleres recreativos y terapias físicas de manera constante.
                                </p>
                                <hr class="hero-card-divider">
                                <a href="/donaciones" class="btn btn-secondary hero-card-cta" onclick={() => onActionClick('Apadrinar')}>
                                        Apadrinar Hoy 🤝
                                </a>
                        </div>
                </div>
        </div>

        <div class="stats-banner">
                <div class="stats-grid">
                        <div class="stat-item">
                                <i class="fa-solid fa-users stat-icon"></i>
                                <span class="stat-number">+120</span>
                                <span class="stat-label">Adultos Mayores Atendidos</span>
                        </div>
                        <div class="stat-divider"></div>
                        <div class="stat-item">
                                <i class="fa-solid fa-seedling stat-icon"></i>
                                <span class="stat-number">11</span>
                                <span class="stat-label">Proyectos Activos</span>
                        </div>
                        <div class="stat-divider"></div>
                        <div class="stat-item">
                                <i class="fa-solid fa-map-location-dot stat-icon"></i>
                                <span class="stat-number">25</span>
                                <span class="stat-label">Municipios de Alcance</span>
                        </div>
                </div>
        </div>
</section>
