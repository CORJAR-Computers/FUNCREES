@echo off
title Iniciando FUNCREES
echo ===================================================
echo   Iniciando Sistema FUNCREES (Backend y Frontend)
echo ===================================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo y asegúrate de marcar "Add python.exe to PATH" durante la instalación.
    pause
    exit /b
)

:: Ir a la carpeta backend
cd /d "%~dp0backend"

:: Verificar que existe el archivo .env
if not exist ".env" (
    echo [AVISO] No se encontro el archivo .env
    echo.
    echo Creando .env desde .env.example...
    echo.
    echo ¡IMPORTANTE! Debes editar backend/.env con tus claves reales
    echo antes de continuar. Presiona Ctrl+C para salir y configurarlo.
    echo.
    copy .env.example .env >nul
    echo Archivo .env creado. Por favor editalo con tus valores.
    echo.
    echo Presiona cualquier tecla para continuar de todas formas...
    pause >nul
)

:: Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual local...
    python -m venv venv
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar dependencias
echo Instalando dependencias necesarias (esto puede tardar unos segundos)...
pip install -r requirements.txt -q

:: Aplicar migraciones
echo Verificando base de datos...
python manage.py migrate --noinput

:: Ir a la raiz del proyecto
cd ..

:: Abrir el frontend en el navegador por defecto
echo Abriendo el sitio web en tu navegador...
start index.html

:: Iniciar el servidor de Django
echo.
echo ===================================================
echo   El servidor backend esta en linea.
echo   Sitio web: file:///%CD%/index.html
echo   Panel de Admin: http://127.0.0.1:8000/admin/
echo.
echo   MANTEN ESTA VENTANA ABIERTA para que el sistema funcione.
echo   Para salir, cierra esta ventana.
echo ===================================================
echo.
cd backend
python manage.py runserver
