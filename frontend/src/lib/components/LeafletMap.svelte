<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import 'leaflet/dist/leaflet.css';

  /** @type {any} */
  let mapInstance;
  /** @type {HTMLDivElement} */
  let mapElement;

  onMount(async () => {
    if (!browser) return;
    const L = (await import('leaflet')).default;

    /** @type {[number, number]} */
    const sincelejoCoords = [9.3046, -75.3906];

    const isDark = document.body.classList.contains('dark-mode');
    const tileUrl = isDark
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

    mapInstance = L.map(mapElement, {
      center: sincelejoCoords,
      zoom: 15,
      zoomControl: true,
      scrollWheelZoom: false
    });

    L.tileLayer(tileUrl, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(mapInstance);

    const redIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    const marker = L.marker(sincelejoCoords, { icon: redIcon }).addTo(mapInstance);
    marker.bindPopup(`
      <div style="font-family: var(--font-body, sans-serif); padding: 0.25rem;">
        <strong style="color: #1b5e20;">🏢 SEDE FUNCREESCOLOMBIA</strong><br>
        <span>Carrera 15b #41c - 07, Sincelejo, Sucre</span><br>
        <small style="color: #555;">NIT: 902036173-3</small>
      </div>
    `).openPopup();
  });

  onDestroy(() => {
    if (mapInstance) {
      mapInstance.remove();
    }
  });
</script>

<div
  bind:this={mapElement}
  class="leaflet-map-container"
  style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0;"
></div>
