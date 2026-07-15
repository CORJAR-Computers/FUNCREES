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
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo  Por favor instala Python desde: https://www.python.org/downloads/
    echo  Marca "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)
echo  [OK] Python detectado

:: Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Node.js no esta instalado o no esta en el PATH.
    echo  Por favor instala Node.js desde: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo  [OK] Node.js detectado

:: ============================================
:: PASO 2: Configurar Backend
:: ============================================
echo.
echo [2/6] Configurando Backend Django...

cd /d "%~dp0backend"

:: Crear entorno virtual si no existe
if not exist "venv" (
    echo  Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo  [OK] Entorno virtual creado
) else (
    echo  [OK] Entorno virtual existente
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar dependencias
echo  Instalando dependencias Python...
pip install -r requirements.txt -q --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  [ERROR] Error al instalar dependencias Python.
    pause
    exit /b 1
)
echo  [OK] Dependencias Python instaladas

:: ============================================
:: PASO 3: Configurar Base de Datos (DEMO LOCAL con SQLite)
:: ============================================
echo.
echo [3/6] Configurando base de datos para demo local...

:: Para demo local SIEMPRE usar DEBUG=True y SQLite — no requiere PostgreSQL
if not exist ".env" (
    echo  Creando .env de DEMO LOCAL con SQLite...
    (
        echo # FUNCREES Colombia - .env DEMO LOCAL
        echo # Generado por demo.bat — NO usar en produccion
        echo DEBUG=True
        echo SECRET_KEY=demo-local-key-funcrees-2025-change-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DATABASE_URL=sqlite:///db.sqlite3
        echo CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
        echo FRONTEND_URL=http://localhost:5500
        echo DEFAULT_FROM_EMAIL=demo@funcreescolombia.org
        echo EMAIL_HOST=smtp.gmail.com
        echo EMAIL_PORT=587
        echo EMAIL_USE_TLS=True
        echo EMAIL_HOST_USER=
        echo EMAIL_HOST_PASSWORD=
        echo WOMPI_ENV=sandbox
        echo WOMPI_PUBLIC_KEY=pub_test_placeholder
        echo WOMPI_PRIVATE_KEY=prv_test_placeholder
        echo WOMPI_INTEGRITY_SECRET=test_integrity_placeholder
        echo ENCRYPTION_KEY=
    ) > .env
    echo  [OK] .env de demo creado (SQLite + DEBUG=True)
) else (
    :: Detectar si el .env existente usa PostgreSQL o DEBUG=False
    findstr /i "DEBUG=False" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [AVISO] El .env existente tiene DEBUG=False (modo produccion).
        echo  Para demo local se necesita DEBUG=True con SQLite.
        echo  Desea usar configuracion temporal de demo? (S=Si / N=Mantener actual)
        set /p usardemo=Respuesta: 
        if /i "%usardemo%"=="S" (
            copy .env .env.bak >nul
            echo  Backup guardado en .env.bak
            (
                echo # FUNCREES Colombia - .env DEMO LOCAL TEMPORAL
                echo # Backup del original guardado en .env.bak
                echo DEBUG=True
                echo SECRET_KEY=demo-local-key-funcrees-2025-change-in-production
                echo ALLOWED_HOSTS=localhost,127.0.0.1
                echo DATABASE_URL=sqlite:///db.sqlite3
                echo CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
                echo FRONTEND_URL=http://localhost:5500
                echo DEFAULT_FROM_EMAIL=demo@funcreescolombia.org
                echo EMAIL_HOST=smtp.gmail.com
                echo EMAIL_PORT=587
                echo EMAIL_USE_TLS=True
                echo EMAIL_HOST_USER=
                echo EMAIL_HOST_PASSWORD=
                echo WOMPI_ENV=sandbox
                echo WOMPI_PUBLIC_KEY=pub_test_placeholder
                echo WOMPI_PRIVATE_KEY=prv_test_placeholder
                echo WOMPI_INTEGRITY_SECRET=test_integrity_placeholder
                echo ENCRYPTION_KEY=
            ) > .env
            echo  [OK] .env temporal de demo creado
        ) else (
            echo  Manteniendo .env existente (puede fallar si PostgreSQL no esta disponible).
        )
    ) else (
        echo  [OK] .env existente detectado
    )
)

:: Ejecutar migraciones
echo  Aplicando migraciones de base de datos...
python manage.py migrate --noinput 2>nul
if %errorlevel% neq 0 (
    echo  [AVISO] Error en migraciones. Continuando...
) else (
    echo  [OK] Base de datos configurada
)

:: Cargar datos de ejemplo si la BD esta vacia
echo  Verificando datos de ejemplo...
python -c "from beneficiaries.models import Beneficiary; print(Beneficiary.objects.count())" 2>nul | findstr "0" >nul
if %errorlevel% equ 0 (
    echo  Cargando datos de ejemplo para la demo...
    python populate_db.py 2>nul
    echo  [OK] Datos de ejemplo cargados
) else (
    echo  [OK] Datos de ejemplo ya existen
)

:: ============================================
:: PASO 4: Configurar Frontend
:: ============================================
echo.
echo [4/6] Configurando Frontend...

cd /d "%~dp0"

:: Verificar si node_modules existe
if not exist "node_modules" (
    echo  Instalando dependencias npm...
    call npm install --silent 2>nul
    echo  [OK] Dependencias npm instaladas
) else (
    echo  [OK] Dependencias npm existentes
)

:: Verificar que serve este disponible
echo  Verificando servidor estatico (serve)...
npx serve --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando serve para la demo...
    call npm install -g serve --silent 2>nul
    if %errorlevel% neq 0 (
        echo  [AVISO] No se pudo instalar serve globalmente. Usando npx serve (se descargara).
    )
)
echo  [OK] Servidor estatico listo

:: ============================================
:: PASO 5: Verificar Puertos e Iniciar Servidores
:: ============================================
echo.
echo [5/6] Verificando puertos e iniciando servidores...

:: Verificar si el puerto 8000 esta en uso
netstat -an | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [AVISO] Puerto 8000 ya esta en uso.
    echo  Desea continuar de todas formas? (S/N)
    set /p respuesta=
    if /i "%respuesta%" neq "S" (
        echo  Operacion cancelada.
        pause
        exit /b 1
    )
) else (
    echo  [OK] Puerto 8000 disponible
)

:: Verificar si el puerto 5500 esta en uso
netstat -an | findstr ":5500 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [AVISO] Puerto 5500 ya esta en uso.
    echo  Desea continuar de todas formas? (S/N)
    set /p respuesta2=
    if /i "%respuesta2%" neq "S" (
        echo  Operacion cancelada.
        pause
        exit /b 1
    )
) else (
    echo  [OK] Puerto 5500 disponible
)

:: --- INICIAR BACKEND --- ruta absoluta con %~dp0 para evitar errores de directorio
echo.
echo  Iniciando Backend Django en puerto 8000...
start "FUNCREES Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && echo [FUNCREES] Backend iniciado en http://localhost:8000 && python manage.py runserver 0.0.0.0:8000 --noreload"

:: Esperar a que el backend arranque (5 segundos)
echo  Esperando arranque del backend...
timeout /t 5 /nobreak >nul

:: --- INICIAR FRONTEND --- ruta absoluta
echo  Iniciando Frontend en puerto 5500...
start "FUNCREES Frontend" cmd /k "cd /d "%~dp0" && echo [FUNCREES] Frontend iniciado en http://localhost:5500 && npx serve . -p 5500 --no-clipboard --cors"

:: Esperar a que el frontend arranque
timeout /t 3 /nobreak >nul

:: ============================================
:: PASO 6: Abrir Navegador
:: ============================================
echo.
echo [6/6] Abriendo navegador...
start http://localhost:5500

:: ============================================
:: INSTRUCCIONES FINALES
:: ============================================
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║               FUNCREES COLOMBIA - DEMO ACTIVO               ║
echo  ╠═══════════════════════════════════════════════════════════════╣
echo  ║                                                              ║
echo  ║  Frontend:  http://localhost:5500                            ║
echo  ║  API:       http://localhost:8000/api/                       ║
echo  ║  Admin:     http://localhost:8000/admin/                     ║
echo  ║                                                              ║
echo  ╠═══════════════════════════════════════════════════════════════╣
echo  ║  DEMO: DEBUG=True + SQLite (sin necesidad de PostgreSQL)    ║
echo  ╠═══════════════════════════════════════════════════════════════╣
echo  ║  Para crear usuario Admin de la demo:                       ║
echo  ║  En la ventana "FUNCREES Backend" ejecuta:                  ║
echo  ║  python manage.py createsuperuser                           ║
echo  ╠═══════════════════════════════════════════════════════════════╣
echo  ║  NO CIERRES ESTA VENTANA durante la demo                    ║
echo  ║  Al presionar una tecla se detendran los servidores         ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Mantener ventana abierta — al presionar tecla detener servidores
pause

:: Limpiar procesos al cerrar
echo.
echo  Deteniendo servidores...
taskkill /F /FI "WINDOWTITLE eq FUNCREES Backend" /IM python.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FUNCREES Frontend" /IM node.exe >nul 2>&1
echo  Servidores detenidos. Hasta pronto.
timeout /t 2 /nobreak >nul
