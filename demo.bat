@echo off
title FUNCREES Colombia - Demo Local
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║        FUNCREES COLOMBIA - MODO DEMOSTRACIÓN LOCAL         ║
echo  ║        Fundación Crece Una Esperanza Social                ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: ============================================
:: PASO 1: Verificar prerequisitos
:: ============================================
echo [1/6] Verificando prerequisitos...

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python no está instalado o no está en el PATH.
    echo  Por favor instala Python desde: https://www.python.org/downloads/
    echo  Marca "Add python.exe to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)
echo  ✓ Python detectado

:: Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Node.js no está instalado o no está en el PATH.
    echo  Por favor instala Node.js desde: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo  ✓ Node.js detectado

:: ============================================
:: PASO 2: Configurar Backend
:: ============================================
echo.
echo [2/6] Configurando Backend Django...

cd /d "%~dp0backend"

:: Crear entorno virtual si no existe
if not exist "venv" (
    echo  → Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo  ✓ Entorno virtual creado
) else (
    echo  ✓ Entorno virtual existente
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar dependencias
echo  → Instalando dependencias Python...
pip install -r requirements.txt -q --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  [ERROR] Error al instalar dependencias Python.
    pause
    exit /b 1
)
echo  ✓ Dependencias Python instaladas

:: ============================================
:: PASO 3: Configurar Base de Datos
:: ============================================
echo.
echo [3/6] Configurando base de datos...

:: Verificar si existe .env, si no copiar desde .env.example
if not exist ".env" (
    echo  → Creando archivo .env desde plantilla...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo  ✓ Archivo .env creado (usa valores por defecto para demo)
    ) else (
        echo  [AVISO] No se encontró .env.example, usando configuración por defecto
    )
)

:: Ejecutar migraciones
echo  → Aplicando migraciones...
python manage.py migrate --noinput 2>nul
if %errorlevel% neq 0 (
    echo  [AVISO] Error en migraciones, continuando de todas formas...
)
echo  ✓ Base de datos configurada

:: Cargar datos de ejemplo si la BD está vacía
echo  → Verificando datos de ejemplo...
python -c "from beneficiaries.models import Beneficiary; print(Beneficiary.objects.count())" 2>nul | findstr "0" >nul
if %errorlevel% equ 0 (
    echo  → Cargando datos de ejemplo...
    python populate_db.py 2>nul
    echo  ✓ Datos de ejemplo cargados
) else (
    echo  ✓ Datos de ejemplo ya existen
)

:: ============================================
:: PASO 4: Configurar Frontend
:: ============================================
echo.
echo [4/6] Configurando Frontend...

cd /d "%~dp0"

:: Verificar si node_modules existe
if not exist "node_modules" (
    echo  → Instalando dependencias npm...
    call npm install --silent 2>nul
    echo  ✓ Dependencias npm instaladas
) else (
    echo  ✓ Dependencias npm existentes
)

:: ============================================
:: PASO 5: Verificar Puertos y Iniciar Servidores
:: ============================================
echo.
echo [5/6] Verificando puertos e iniciando servidores...

:: Verificar si el puerto 8000 está en uso
netstat -an | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [AVISO] Puerto 8000 ya está en uso.
    echo  ¿Deseas continuar de todas formas? (S/N)
    set /p respuesta=
    if /i "%respuesta%" neq "S" (
        echo  Operación cancelada.
        pause
        exit /b 1
    )
) else (
    echo  ✓ Puerto 8000 disponible
)

:: Verificar si el puerto 5500 está en uso
netstat -an | findstr ":5500 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [AVISO] Puerto 5500 ya está en uso.
    echo  ¿Deseas continuar de todas formas? (S/N)
    set /p respuesta2=
    if /i "%respuesta2%" neq "S" (
        echo  Operación cancelada.
        pause
        exit /b 1
    )
) else (
    echo  ✓ Puerto 5500 disponible
)

:: Crear ventana para el backend
echo.
echo  → Iniciando Backend Django (puerto 8000)...
start "FUNCREES Backend" cmd /c "cd backend && call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

:: Esperar un momento para que el backend arranque
timeout /t 4 /nobreak >nul

:: Crear ventana para el frontend
echo  → Iniciando Frontend (puerto 5500)...
start "FUNCREES Frontend" cmd /c "npx serve . -p 5500 --no-clipboard --cors"

:: Esperar un momento para que el frontend arranque
timeout /t 3 /nobreak >nul

:: ============================================
:: PASO 6: Abrir Navegador
:: ============================================
echo.
echo [6/6] Abriendo navegador...

:: Abrir el frontend en el navegador
start http://localhost:5500

:: ============================================
:: INSTRUCCIONES FINALES
:: ============================================
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║              ¡SISTEMA FUNCREES INICIADO!                   ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║                                                            ║
echo  ║  🌐 Frontend:   http://localhost:5500                      ║
echo  ║  🔧 Backend:    http://localhost:8000/api/                 ║
echo  ║  👨‍💼 Admin:      http://localhost:8000/admin/                ║
echo  ║                                                            ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  INSTRUCCIONES PARA LA DEMOSTRACIÓN:                      ║
echo  ║                                                            ║
echo  ║  1. El sitio web se abrirá automáticamente en tu navegador║
echo  ║  2. Puedes navegar por todas las secciones del sitio       ║
echo  ║  3. Para mostrar el Admin, ve a: /admin/                  ║
echo  ║     Usuario: admin | Contraseña: (la que configuraste)    ║
echo  ║                                                            ║
echo  ║  ⚠️  NO CIERRES ESTA VENTANA mientras haces la demo       ║
echo  ║                                                            ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Para DETENER el sistema:                                  ║
echo  ║  1. Cierra esta ventana (se cerrarán los servidores)       ║
echo  ║  2. Cierra las ventanas "FUNCREES Backend" y "Frontend"    ║
echo  ║  3. O ejecuta: taskkill /F /IM python.exe & taskkill /F /IM node.exe ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: Mantener esta ventana abierta y limpiar al cerrar
pause
:: Limpiar procesos al cerrar esta ventana
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FUNCREES*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq FUNCREES*" >nul 2>&1
