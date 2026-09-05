<script>
  import { toast } from '$lib/stores/toast.svelte.js';
</script>

<svelte:head>
  <title>Quiénes Somos | Fundación Funcrees Colombia</title>
  <meta name="description" content="Conoce la misión, visión, valores y pilares de acción de la Fundación Funcrees en Sincelejo, Sucre. Comprometidos con el desarrollo integral y digno." />
</svelte:head>

<section id="quienes-somos" class="view-section active">
  <div class="section">
    <div class="section-header">
      <span class="section-subtitle">Identidad Corporativa</span>
      <h1 class="section-title">Quiénes Somos: Compromiso con el Cambio Social</h1>
      <p class="section-description">
        Una organización Sincelejana que trabaja con transparencia y ética para dignificar la vida en la edad dorada y transformar comunidades.
      </p>
    </div>

    <div class="identidad-grid">
      <div class="identidad-text-block">
        <p>
          La <strong>Fundación Crece una Esperanza Social (FUNCREESCOLOMBIA)</strong> es una entidad sin ánimo de lucro (ESAL)
          con personería jurídica y autonomía administrativa, nacida en Sincelejo, Sucre. Somos una organización privada y pluralista
          guiada por la ética, el respeto a la dignidad y el compromiso social.
        </p>
        <p>
          Nos consolidamos como un motor de transformación social. Diseñamos, gestionamos y ejecutamos soluciones innovadoras
          para promover el desarrollo integral del ser humano en todas las etapas de su vida; desde la infancia hasta la sabiduría
          de nuestras personas mayores, convencidos de que cada etapa debe vivirse con dignidad, propósito y autonomía.
        </p>
        <p>
          <strong>NIT:</strong> 902036173-3 &nbsp;&bull;&nbsp; <strong>Domicilio:</strong> Carrera 15b #41c - 07, Sincelejo, Sucre
        </p>
        <div style="display:flex; gap:1.5rem; margin-top:2rem; flex-wrap:wrap;">
          <div style="display:flex; align-items:center; gap:0.5rem; color:var(--primary-dark); font-weight:700;">
            <i class="fa-solid fa-shield-check" style="font-size:1.5rem;"></i> Transparencia
          </div>
          <div style="display:flex; align-items:center; gap:0.5rem; color:var(--primary-dark); font-weight:700;">
            <i class="fa-solid fa-heart-pulse" style="font-size:1.5rem;"></i> Solidaridad Ética
          </div>
        </div>
      </div>
      <div class="identidad-image-grid">
        <div class="identidad-img" style="background-image: url('https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600&h=400&fit=crop'); background-size:cover; background-position:center;"></div>
        <div class="identidad-img" style="background-image: url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&h=400&fit=crop'); background-size:cover; background-position:center;"></div>
        <div class="identidad-img identidad-img-large" style="background-image: url('https://images.unsplash.com/photo-1592477353930-b99b380f70a5?w=800&h=500&fit=crop'); background-size:cover; background-position:center;"></div>
      </div>
    </div>

    <!-- Misión & Visión -->
    <div class="mision-vision-container">
      <div class="mv-card mision-card">
        <div class="mv-header">
          <div class="mv-icon"><i class="fa-solid fa-hands-holding-child"></i></div>
          <h3 class="mv-title">Nuestra Misión</h3>
        </div>
        <p class="mv-text">
          Despertar el potencial humano y restituir la dignidad de quienes más lo necesitan. Transformamos la vulnerabilidad en oportunidad
          mediante soluciones sociales innovadoras que promueven el desarrollo integral del ser humano en todas las etapas de su vida,
          bajo principios de ética, empatía y respeto.
        </p>
      </div>
      <div class="mv-card vision-card">
        <div class="mv-header">
          <div class="mv-icon"><i class="fa-solid fa-road-circle-check"></i></div>
          <h3 class="mv-title">Nuestra Visión 2030</h3>
        </div>
        <p class="mv-text">
          Ser reconocidos como un referente líder a nivel nacional en el cuidado afectivo de adultos mayores y en la formación de líderes con propósito.
          Nos consolidaremos como un motor de cambio que fortalece comunidades autónomas, productivas y resilientes, destacándonos por nuestra gestión,
          transparencia y desarrollo sostenible.
        </p>
      </div>
    </div>

    <!-- Valores Fundamentales -->
    <div style="text-align:center; margin-bottom: 3.5rem;">
      <span class="section-subtitle">Nuestros Valores</span>
      <h2 style="color:var(--secondary)">Principios que Guían Nuestro Camino</h2>
    </div>
    <div class="valores-grid">
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-house-heart"></i></div>
        <h4 class="valor-title">Familia</h4>
        <p class="valor-desc">Entender a la comunidad como un núcleo esencial de apoyo, cuidado y afecto.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-people-group"></i></div>
        <h4 class="valor-title">Unión</h4>
        <p class="valor-desc">Trabajar en sinergia con todos los sectores para multiplicar el impacto social.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-hands-holding"></i></div>
        <h4 class="valor-title">Nobleza</h4>
        <p class="valor-desc">Actuar con rectitud, transparencia y un corazón dispuesto al servicio.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-shield-check"></i></div>
        <h4 class="valor-title">Compromiso</h4>
        <p class="valor-desc">Entregarse con firmeza a la transformación positiva de las realidades sociales.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-scale-balanced"></i></div>
        <h4 class="valor-title">Respeto</h4>
        <p class="valor-desc">Reconocer y salvaguardar la dignidad y el valor de cada etapa de la vida.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-heart-pulse"></i></div>
        <h4 class="valor-title">Empatía</h4>
        <p class="valor-desc">Conectarse de forma genuina con el otro para comprender y atender sus necesidades.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-seedling"></i></div>
        <h4 class="valor-title">Esperanza</h4>
        <p class="valor-desc">Creer firmemente en la superación humana y en la construcción de un futuro digno.</p>
      </div>
      <div class="valor-card">
        <div class="valor-icon"><i class="fa-solid fa-hands-holding-circle"></i></div>
        <h4 class="valor-title">Solidaridad</h4>
        <p class="valor-desc">Actuar como fuerza motriz para brindar respaldo oportuno a los más vulnerables.</p>
      </div>
    </div>

    <!-- Objetivos Estratégicos -->
    <div class="objetivos-box">
      <div class="objetivos-grid">
        <div>
          <span class="section-subtitle">Objetivos Estratégicos</span>
          <h2 style="color:var(--secondary); margin-bottom:1.5rem;">Cuatro Pilares de Acción</h2>
          <p style="color:var(--text-muted); margin-bottom: 2rem;">
            Para materializar nuestra visión, enfocamos nuestra gestión en cuatro pilares fundamentales que garantizan que cada peso donado genere un impacto social visible y duradero.
          </p>
          <a href="/contacto" class="btn btn-primary">Quiero ser Voluntario</a>
        </div>
        <div>
          <ul class="objetivos-list">
            <li class="objetivo-item">
              <div class="objetivo-check">✓</div>
              <span class="objetivo-text"><strong>Desarrollo Integral y Equidad:</strong> Impulsar el crecimiento del individuo y su entorno mediante proyectos de asistencia y formación, construyendo una sociedad más justa y solidaria.</span>
            </li>
            <li class="objetivo-item">
              <div class="objetivo-check">✓</div>
              <span class="objetivo-text"><strong>Productividad y Autonomía:</strong> Diseñar y ejecutar proyectos que generen empleo e ingresos, promoviendo modelos sostenibles que permitan la independencia económica comunitaria.</span>
            </li>
            <li class="objetivo-item">
              <div class="objetivo-check">✓</div>
              <span class="objetivo-text"><strong>Bienestar y Cultura:</strong> Fortalecer el bienestar social e identidad cultural a través del arte, la recreación y el deporte como herramientas clave de cohesión y salud mental.</span>
            </li>
            <li class="objetivo-item">
              <div class="objetivo-check">✓</div>
              <span class="objetivo-text"><strong>Generación de Conocimiento:</strong> Liderar espacios académicos —foros, seminarios y conferencias— para fomentar el intercambio de saberes e incidir en políticas sociales de impacto real.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>
