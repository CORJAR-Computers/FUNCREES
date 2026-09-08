<script lang="ts">
        import { page } from '$app/state';
        import { onMount } from 'svelte';

        let isMenuOpen = $state(false);
        let isDarkMode = $state(false);

        function toggleMenu(): void {
                isMenuOpen = !isMenuOpen;
        }

        function closeMenu(): void {
                isMenuOpen = false;
        }

        function isActive(path: string): boolean {
                return page.url.pathname === path;
        }

        function toggleTheme(): void {
                isDarkMode = !isDarkMode;
                if (isDarkMode) {
                        document.body.classList.add('dark-mode');
                        localStorage.setItem('funcrees-theme', 'dark');
                } else {
                        document.body.classList.remove('dark-mode');
                        localStorage.setItem('funcrees-theme', 'light');
                }
        }

        onMount(() => {
                const savedTheme = localStorage.getItem('funcrees-theme');
                if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                        isDarkMode = true;
                        document.body.classList.add('dark-mode');
                }

                function handleKeyDown(e: KeyboardEvent): void {
                        if (e.key === 'Escape' && isMenuOpen) {
                                closeMenu();
                        }
                }

                window.addEventListener('keydown', handleKeyDown);
                return () => {
                        window.removeEventListener('keydown', handleKeyDown);
                };
        });
</script>

<header class="header">
        <div class="header-container">
                <a href="/" class="logo-wrapper" onclick={closeMenu}>
                        <!-- Logo optimizado: 18 KB WebP (antes Logo.png de 2.5 MB en cada página).
                             width/height evitan CLS durante la carga. -->
                        <img
                                class="logo-img"
                                src="/assets/logo-funcrees.webp"
                                alt="Logo Funcrees"
                                width="360"
                                height="240"
                                style="height: 50px; width: auto; object-fit: contain;"
                        >
                        <div class="logo-text">
                                <span class="logo-title">FUNCREES</span>
                                <span class="logo-subtitle">Crece Una Esperanza</span>
                        </div>
                </a>

                <button
                        class="menu-toggle"
                        class:active={isMenuOpen}
                        aria-label={isMenuOpen ? "Cerrar menú de navegación" : "Abrir menú de navegación"}
                        aria-expanded={isMenuOpen}
                        onclick={toggleMenu}
                >
                        {#if isMenuOpen}
                                <i class="fa-solid fa-xmark"></i>
                        {:else}
                                <i class="fa-solid fa-bars"></i>
                        {/if}
                </button>

                <nav class:active={isMenuOpen} aria-label="Navegación principal">
                        <ul class="nav-menu" class:active={isMenuOpen}>
                                <li><a class="nav-link" class:active={isActive('/')} href="/" onclick={closeMenu}>Inicio</a></li>
                                <li><a class="nav-link" class:active={isActive('/quienes-somos')} href="/quienes-somos" onclick={closeMenu}>Quiénes Somos</a></li>
                                <li><a class="nav-link" class:active={isActive('/proyectos')} href="/proyectos" onclick={closeMenu}>Nuestros Proyectos</a></li>
                                <li><a class="nav-link" class:active={isActive('/numeros')} href="/numeros" onclick={closeMenu}>Nuestros Números</a></li>
                                <li><a class="nav-link" class:active={isActive('/historias')} href="/historias" onclick={closeMenu}>Historias de Vida</a></li>
                                <li><a class="nav-link" class:active={isActive('/donaciones')} href="/donaciones" onclick={closeMenu}>Donaciones y Aliados</a></li>
                                <li><a class="nav-link" class:active={isActive('/eventos')} href="/eventos" onclick={closeMenu}>Eventos</a></li>
                                <li><a class="nav-link" class:active={isActive('/contacto')} href="/contacto" onclick={closeMenu}>Contactar</a></li>
                                <li class="theme-toggle-li">
                                        <button class="theme-toggle" onclick={toggleTheme} aria-label="Alternar tema oscuro" title="Alternar Modo Oscuro">
                                                {#if isDarkMode}
                                                        <svg class="icon-svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                                <circle cx="12" cy="12" r="5"></circle>
                                                                <line x1="12" y1="1" x2="12" y2="3"></line>
                                                                <line x1="12" y1="21" x2="12" y2="23"></line>
                                                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                                                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                                                                <line x1="1" y1="12" x2="3" y2="12"></line>
                                                                <line x1="21" y1="12" x2="23" y2="12"></line>
                                                                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                                                                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                                                        </svg>
                                                {:else}
                                                        <svg class="icon-svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                                                        </svg>
                                                {/if}
                                        </button>
                                </li>
                        </ul>
                </nav>
        </div>

        {#if isMenuOpen}
                <button
                        type="button"
                        class="nav-backdrop"
                        aria-label="Cerrar menú de navegación"
                        onclick={closeMenu}
                ></button>
        {/if}
</header>
