#!/usr/bin/env python3
"""
=============================================================================
apply_frontend_patches.py — Parches de seguridad para app.js de FUNCREES
=============================================================================

Este script aplica automáticamente los parches de seguridad al archivo
app.js del proyecto Fundación Funcrees Colombia.

CORRECCIONES APLICADAS:
  - PATCH 1:  XSS en toast de notificaciones                [CRÍTICO]
  - PATCH 2:  XSS en comprobante PSE                        [CRÍTICO]
  - PATCH 3:  XSS en comprobante Bancolombia                [CRÍTICO]
  - PATCH 4:  XSS en modal de compra de entradas            [CRÍTICO]
  - PATCH 5:  XSS en comprobante de compra de entrada       [CRÍTICO]
  - PATCH 6:  XSS en enlace de WhatsApp                     [ALTO]
  - PATCH 7:  Eliminación de onclick en línea / CSP         [ALTO]

USO:
  python3 apply_frontend_patches.py [ruta_a_app.js]

  Si no se especifica ruta, busca ./app.js en el directorio actual.

RESULTADO:
  Genera app.js.parcheado con las correcciones aplicadas.
  El archivo original NO se modifica (se crea copia de seguridad .bak).
  Además genera:
    - bloque_delegacion_eventos.js  → código a insertar manualmente
    - parche_informe.txt            → informe detallado de cambios

Dependencias: Python 3.6+ (solo librería estándar)
=============================================================================
"""

import os
import re
import sys
import shutil
import datetime


# =============================================================================
# DEFINICIÓN DE PARCHES
# =============================================================================
# Dos tipos de parches:
#   1. LITERALES: tupla (descripción, cadena_búsqueda, cadena_reemplazo)
#      Búsqueda de texto exacto. Útil cuando la cadena es única y conocida.
#
#   2. REGEX: tupla (descripción, patrón_regex, cadena_reemplazo, True)
#      El cuarto elemento indica que es regex. Útil para patrones flexibles.
# =============================================================================

PARCHES_LITERALES = [
    # ---------------------------------------------------------------------------
    # PATCH 1 — XSS en notificación toast (línea ~69)
    # ---------------------------------------------------------------------------
    # La función showToast() inserta `message` directamente en innerHTML.
    # Si un atacante controla el mensaje (ej. desde la API), puede inyectar
    # HTML/JS arbitrario. Se envuelve con sanitizeHTML().
    # ---------------------------------------------------------------------------
    (
        "PATCH 1 [CRÍTICO]: XSS en toast — envolver ${message} con sanitizeHTML()",
        'toast.innerHTML = `<span style="font-size:1.2rem;font-weight:800;flex-shrink:0;">${iconMap[type] || \'✓\'}</span><span>${message}</span>`;',
        'toast.innerHTML = `<span style="font-size:1.2rem;font-weight:800;flex-shrink:0;">${iconMap[type] || \'✓\'}</span><span>${sanitizeHTML(message)}</span>`;',
    ),

    # ---------------------------------------------------------------------------
    # PATCH 4 — XSS en modal de compra de entradas (líneas ~1676-1677)
    # ---------------------------------------------------------------------------
    # El modal de checkout para comprar entradas muestra el título y la
    # descripción del evento obtenidos de la API. Si la API está comprometida
    # o devuelve datos maliciosos, se ejecuta código arbitrario en el navegador
    # de todos los visitantes.
    # ---------------------------------------------------------------------------
    (
        "PATCH 4 [CRÍTICO]: XSS en modal de entradas — sanitizar ${ev.titulo}",
        '<h3 class="text-lg font-bold mb-2" style="color:var(--primary)">${ev.titulo}</h3>',
        '<h3 class="text-lg font-bold mb-2" style="color:var(--primary)">${sanitizeHTML(ev.titulo)}</h3>',
    ),

    (
        "PATCH 4b [CRÍTICO]: XSS en modal de entradas — sanitizar ${ev.desc}",
        '<p class="text-sm mb-4" style="color:var(--text-secondary)">${ev.desc}</p>',
        '<p class="text-sm mb-4" style="color:var(--text-secondary)">${sanitizeHTML(ev.desc)}</p>',
    ),

    # ---------------------------------------------------------------------------
    # PATCH 6 — XSS en enlace de WhatsApp (línea ~1779)
    # ---------------------------------------------------------------------------
    # El título del evento se incluye en la URL de WhatsApp. Un título
    # manipulado podría alterar parámetros de la URL. Se sanitiza como
    # defensa en profundidad.
    # ---------------------------------------------------------------------------
    (
        "PATCH 6 [ALTO]: XSS en WhatsApp — sanitizar título del evento",
        'encodeURIComponent(ev.titulo)',
        'encodeURIComponent(sanitizeHTML(ev.titulo))',
    ),
]


# Parches que usan regex (para patrones que pueden variar en espacios/estilos)
PARCHES_REGEX = [
    # ---------------------------------------------------------------------------
    # PATCH 2 — XSS en comprobante de donación PSE (líneas ~1531-1546)
    # ---------------------------------------------------------------------------
    # En la confirmación de donación vía PSE, los campos nombre y email del
    # donante se insertan en innerHTML sin sanitizar. Un donante malicioso
    # podría registrar un nombre como <img src=x onerror=alert(1)>.
    # ---------------------------------------------------------------------------
    (
        "PATCH 2 [CRÍTICO]: XSS en comprobante PSE — sanitizar ${nombre}",
        r'\$\{nombre\}(<\/strong>)',
        r'${sanitizeHTML(nombre)}\1',
    ),

    (
        "PATCH 2b [CRÍTICO]: XSS en comprobante PSE — sanitizar ${email}",
        r'\$\{email\}(<\/strong>)',
        r'${sanitizeHTML(email)}\1',
    ),

    # ---------------------------------------------------------------------------
    # PATCH 3 — XSS en comprobante de donación Bancolombia (líneas ~1555-1570)
    # ---------------------------------------------------------------------------
    # Misma vulnerabilidad: nombre y título del evento sin sanitizar en la
    # rama de pago por Bancolombia.
    # ---------------------------------------------------------------------------
    # NOTA: Los parches 3 se aplican después de los parches 2, por lo que
    # solo afectarán las ocurrencias restantes en la sección de Bancolombia.
    # ---------------------------------------------------------------------------
    (
        "PATCH 3 [CRÍTICO]: XSS en comprobante Bancolombia — sanitizar ${nombre} (2da ocurrencia)",
        r'\$\{nombre\}(<\/strong>)',
        r'${sanitizeHTML(nombre)}\1',
    ),

    (
        "PATCH 3b [CRÍTICO]: XSS en comprobante Bancolombia — sanitizar ${ev.titulo} en referencia",
        r'\$\{ev\.titulo\}(<\/strong>)',
        r'${sanitizeHTML(ev.titulo)}\1',
    ),

    # ---------------------------------------------------------------------------
    # PATCH 5 — XSS en comprobante de compra de entrada (líneas ~1808-1823)
    # ---------------------------------------------------------------------------
    # Después de la compra exitosa de una entrada, se muestra un comprobante
    # con el título del evento sin sanitizar. Si PATCH 4 ya sanitizó la
    # primera ocurrencia, este parche captura la segunda en el comprobante.
    # ---------------------------------------------------------------------------
    (
        "PATCH 5 [CRÍTICO]: XSS en comprobante de entrada — sanitizar ${ev.titulo} (2da ocurrencia)",
        r'\$\{ev\.titulo\}(<\/strong>)',
        r'${sanitizeHTML(ev.titulo)}\1',
    ),

    # ---------------------------------------------------------------------------
    # PATCH 7 — Eliminar onclick en línea para compatibilidad CSP
    # ---------------------------------------------------------------------------
    # Los atributos onclick= dentro de innerHTML requieren 'unsafe-inline' en
    # la directiva script-src de la CSP. Al eliminarlos y usar delegación de
    # eventos con addEventListener (bloque separado), se fortalece la política
    # CSP y se permite eventualmente quitar 'unsafe-inline'.
    #
    # Se eliminan los onclick de los tres tabs del checkout. Los data-tab-type
    # ya existen y serán usados por la delegación de eventos.
    # ---------------------------------------------------------------------------
    (
        "PATCH 7a [ALTO]: Eliminar onclick inline de pestaña apadrinamiento",
        r'''(class="checkout-tab"\s+)onclick="openDonationModal\('apadrinamiento',\s*checkoutModalState\.preselectedAbuelito\)"(\s+)''',
        r'\1\2',
    ),

    (
        "PATCH 7b [ALTO]: Eliminar onclick inline de pestaña donación",
        r'''(class="checkout-tab"\s+)onclick="openDonationModal\('donacion'\)"(\s+)''',
        r'\1\2',
    ),

    (
        "PATCH 7c [ALTO]: Eliminar onclick inline de pestaña patrocinio",
        r'''(class="checkout-tab"\s+)onclick="openDonationModal\('patrocinio'\)"(\s+)''',
        r'\1\2',
    ),
]


# =============================================================================
# FUNCIÓN PRINCIPAL DE APLICACIÓN DE PARCHES
# =============================================================================

def aplicar_parches(ruta_origen: str) -> bool:
    """
    Lee el archivo app.js original, aplica todos los parches definidos
    y guarda el resultado como app.js.parcheado.

    Retorna True si todos los parches se aplicaron correctamente.
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lineas_cambio = []  # Para el informe

    print(f"\n{'='*70}")
    print(f"  APLICANDO PARCHES DE SEGURIDAD A: {ruta_origen}")
    print(f"  Fecha: {timestamp}")
    print(f"{'='*70}\n")

    # --- Leer archivo original ---
    try:
        with open(ruta_origen, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {ruta_origen}")
        print('  Uso: python3 apply_frontend_patches.py [ruta_a_app.js]')
        return False
    except Exception as e:
        print(f"[ERROR] Leyendo archivo: {e}")
        return False

    lineas_originales = contenido.splitlines(keepends=True)
    contenido_original = contenido
    parches_aplicados = 0
    parches_fallidos = []

    # --- Aplicar parches literales ---
    print("  --- Parches literales ---")
    for descripcion, busqueda, reemplazo in PARCHES_LITERALES:
        if busqueda in contenido:
            pos_antes = contenido.find(busqueda)
            linea_num = contenido[:pos_antes].count('\n') + 1
            contenido = contenido.replace(busqueda, reemplazo, 1)
            parches_aplicados += 1
            lineas_cambio.append(f"  Línea ~{linea_num}: {descripcion}")
            print(f"  ✓ {descripcion} (línea ~{linea_num})")
        else:
            parches_fallidos.append(descripcion)
            print(f"  ✗ NO ENCONTRADO: {descripcion}")

    # --- Aplicar parches regex ---
    print("\n  --- Parches regex ---")
    for parche in PARCHES_REGEX:
        descripcion = parche[0]
        patron = parche[1]
        reemplazo = parche[2]

        coincidencias = list(re.finditer(patron, contenido))
        if coincidencias:
            # Aplicar solo la primera ocurrencia para cada parche
            match = coincidencias[0]
            linea_num = contenido[:match.start()].count('\n') + 1
            contenido = re.sub(patron, reemplazo, contenido, count=1)
            parches_aplicados += 1
            total_coincidencias = len(coincidencias)
            nota = f" ({total_coincidencias} ocurrencia(s) en el archivo, se parcheó la primera)"
            lineas_cambio.append(f"  Línea ~{linea_num}: {descripcion}{nota}")
            print(f"  ✓ {descripcion} (línea ~{linea_num}){nota}")
        else:
            parches_fallidos.append(descripcion)
            print(f"  ✗ NO ENCONTRADO: {descripcion}")

    # --- Verificar si hubo cambios ---
    if contenido == contenido_original:
        print(f"\n[AVISO] No se detectaron cambios.")
        print("  Posibles causas:")
        print("    - El archivo ya está parcheado")
        print("    - Los patrones de búsqueda no coinciden con el código actual")
        print("    - El archivo no es la versión esperada de app.js")
        return False

    # --- Crear backup del original ---
    ruta_salida = ruta_origen.replace('.js', '.js.parcheado')
    ruta_backup = ruta_origen + '.bak'

    if not os.path.exists(ruta_backup):
        shutil.copy2(ruta_origen, ruta_backup)
        print(f"\n  💾 Copia de seguridad creada: {ruta_backup}")

    # --- Escribir archivo parcheado ---
    try:
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n  📄 Archivo parcheado generado: {ruta_salida}")
    except Exception as e:
        print(f"\n[ERROR] Escribiendo archivo parcheado: {e}")
        return False

    # --- Generar bloque de delegación de eventos ---
    ruta_bloque = generar_bloque_delegacion(ruta_salida)

    # --- Generar informe ---
    generar_informe(ruta_salida, timestamp, parches_aplicados,
                    len(PARCHES_LITERALES) + len(PARCHES_REGEX),
                    parches_fallidos, lineas_cambio, ruta_bloque)

    # --- Resumen en consola ---
    total = len(PARCHES_LITERALES) + len(PARCHES_REGEX)
    print(f"\n{'='*70}")
    print(f"  RESUMEN:")
    print(f"    Parches aplicados:   {parches_aplicados}/{total}")
    print(f"    Parches fallidos:    {len(parches_fallidos)}")
    print(f"    Archivo salida:      {ruta_salida}")
    print(f"    Archivo backup:      {ruta_backup}")
    print(f"    Bloque delegación:   {ruta_bloque}")
    print(f"    Informe:             parche_informe.txt")
    print(f"{'='*70}\n")

    if parches_fallidos:
        print("  ⚠ Parches que no se pudieron aplicar (requieren revisión manual):")
        for pf in parches_fallidos:
            print(f"    - {pf}")
        print()

    # --- Instrucciones post-aplicación ---
    print("  SIGUIENTES PASOS:")
    print(f"    1. Revisar {ruta_salida} y verificar los cambios")
    print(f"    2. Insertar el contenido de {ruta_bloque} en app.js")
    print("       (después de la asignación de checkoutContent.innerHTML)")
    print(f"    3. Probar la aplicación exhaustivamente")
    print(f"    4. Reemplazar app.js original con la versión parcheada")
    print()

    return parches_fallidos == []


# =============================================================================
# BLOQUE DE DELEGACIÓN DE EVENTOS
# =============================================================================
# Este bloque debe insertarse manualmente en app.js, inmediatamente después
# de la línea donde se asigna checkoutContent.innerHTML dentro de la función
# que renderiza las pestañas del checkout.
#
# Los data-tab-type ya existen en el HTML de las pestañas. Este código
# las conecta con addEventListener en lugar de onclick inline.
# =============================================================================

BLOQUE_DELEGACION_EVENTOS = """// =============================================================================
// DELEGACIÓN DE EVENTOS PARA PESTAÑAS DE CHECKOUT (PATCH 7)
// =============================================================================
// Insertar este bloque INMEDIATAMENTE DESPUÉS de la línea donde se asigna
// checkoutContent.innerHTML en la función que renderiza el checkout.
//
// Este código reemplaza los onclick inline que fueron eliminados.
// Es compatible con políticas CSP estrictas (sin 'unsafe-inline').
// =============================================================================

document.querySelectorAll('.checkout-tab').forEach(function(tab) {
  tab.addEventListener('click', function(e) {
    e.preventDefault();
    var tabType = this.getAttribute('data-tab-type');
    if (tabType === 'apadrinamiento') {
      openDonationModal('apadrinamiento', checkoutModalState.preselectedAbuelito);
    } else if (tabType === 'donacion') {
      openDonationModal('donacion');
    } else if (tabType === 'patrocinio') {
      openDonationModal('patrocinio');
    }
  });
});
"""


def generar_bloque_delegacion(ruta_salida: str) -> str:
    """
    Escribe el bloque de delegación de eventos en un archivo separado
    para que el desarrollador lo inserte manualmente en la posición correcta.
    Retorna la ruta del archivo generado.
    """
    directorio = os.path.dirname(ruta_salida) or '.'
    ruta_bloque = os.path.join(directorio, 'bloque_delegacion_eventos.js')
    with open(ruta_bloque, 'w', encoding='utf-8') as f:
        f.write(BLOQUE_DELEGACION_EVENTOS)
    print(f"  📋 Bloque de delegación generado: {ruta_bloque}")
    return ruta_bloque


# =============================================================================
# GENERAR INFORME DE PARCHES
# =============================================================================

def generar_informe(ruta_salida, timestamp, aplicados, total, fallidos,
                    lineas_cambio, ruta_bloque):
    """Genera un archivo de texto con el informe detallado de los parches."""
    directorio = os.path.dirname(ruta_salida) or '.'
    ruta_informe = os.path.join(directorio, 'parche_informe.txt')

    with open(ruta_informe, 'w', encoding='utf-8') as f:
        f.write(f"INFORME DE PARCHES DE SEGURIDAD — app.js FUNCREES\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Total de parches: {total}\n")
        f.write(f"Aplicados: {aplicados}\n")
        f.write(f"Fallidos:  {len(fallidos)}\n\n")

        f.write(f"ARCHIVOS GENERADOS:\n")
        f.write(f"  - {ruta_salida}  (archivo parcheado)\n")
        f.write(f"  - {ruta_bloque}  (bloque de delegación de eventos)\n\n")

        if lineas_cambio:
            f.write(f"CAMBIOS APLICADOS:\n")
            f.write(f"{'-'*60}\n")
            for lc in lineas_cambio:
                f.write(f"{lc}\n")
            f.write("\n")

        if fallidos:
            f.write(f"PATCHES FALLIDOS (REQUIEREN REVISIÓN MANUAL):\n")
            f.write(f"{'-'*60}\n")
            for ff in fallidos:
                f.write(f"  - {ff}\n")
            f.write("\n")

        f.write(f"INSTRUCCIONES POST-APLICACIÓN:\n")
        f.write(f"{'-'*60}\n")
        f.write(f"1. Revisar el archivo parcheado y verificar cada cambio.\n")
        f.write(f"2. Insertar el bloque de delegación de eventos en app.js.\n")
        f.write(f"3. Ejecutar pruebas funcionales de:\n")
        f.write(f"   - Donaciones PSE (verificar comprobante)\n")
        f.write(f"   - Donaciones Bancolombia (verificar comprobante)\n")
        f.write(f"   - Compra de entradas a eventos (modal y comprobante)\n")
        f.write(f"   - Pestañas del checkout (apadrinamiento/donación/patrocinio)\n")
        f.write(f"   - Notificaciones toast\n")
        f.write(f"4. Verificar que no hay errores en la consola del navegador.\n")

    print(f"  📝 Informe generado: {ruta_informe}")
    return ruta_informe


# =============================================================================
# FUNCIÓN DE VERIFICACIÓN (DRY RUN)
# =============================================================================

def verificar_parches(ruta_origen: str):
    """
    Simula la aplicación de parches sin modificar archivos.
    Útil para verificar qué parches se aplicarían antes de ejecutar.
    """
    print(f"\n{'='*70}")
    print(f"  MODO VERIFICACIÓN (dry-run) — {ruta_origen}")
    print(f"{'='*70}\n")

    try:
        with open(ruta_origen, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"[ERROR] Leyendo archivo: {e}")
        return

    print("  Parches literales que COINCIDEN:")
    for descripcion, busqueda, reemplazo in PARCHES_LITERALES:
        if busqueda in contenido:
            pos = contenido.find(busqueda)
            linea = contenido[:pos].count('\n') + 1
            print(f"    ✓ {descripcion} (línea ~{linea})")
        else:
            print(f"    ✗ {descripcion}")

    print("\n  Parches regex que COINCIDEN:")
    for parche in PARCHES_REGEX:
        descripcion, patron = parche[0], parche[1]
        coincidencias = list(re.finditer(patron, contenido))
        if coincidencias:
            linea = contenido[:coincidencias[0].start()].count('\n') + 1
            print(f"    ✓ {descripcion} (línea ~{linea}, {len(coincidencias)} ocurrencia(s))")
        else:
            print(f"    ✗ {descripcion}")

    print()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Aplica parches de seguridad al archivo app.js de FUNCREES'
    )
    parser.add_argument(
        'archivo',
        nargs='?',
        default='app.js',
        help='Ruta al archivo app.js (por defecto: ./app.js)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo verificar qué parches se aplicarían, sin modificar archivos'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Sobrescribir el archivo .bak si ya existe'
    )

    args = parser.parse_args()

    if not os.path.exists(args.archivo):
        print(f"[ERROR] No se encontró el archivo: {args.archivo}")
        print('  Uso: python3 apply_frontend_patches.py [ruta_a_app.js]')
        sys.exit(1)

    if args.dry_run:
        verificar_parches(args.archivo)
        sys.exit(0)

    exito = aplicar_parches(args.archivo)
    sys.exit(0 if exito else 1)