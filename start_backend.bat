@echo off
title FUNCREES - Backend Django
cd /d "%~dp0backend"

:: Verificar entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar e instalar dependencias
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

:: Migraciones
python manage.py migrate --noinput

:: Iniciar servidor
echo.
echo ===================================================
echo   BACKEND FUNCREES - Django
echo   http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin/
echo ===================================================
echo.
python manage.py runserver 0.0.0.0:8000

:: Pausar si hay error
if errorlevel 1 (
    echo.
    echo [ERROR] El servidor backend fallo al iniciar.
    pause
)
