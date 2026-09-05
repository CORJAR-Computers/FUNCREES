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
cd backend

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

:: Volver a la raiz
cd ..

echo ===================================================
echo   Iniciando Servidor Backend y Frontend SvelteKit...
echo ===================================================
echo.
echo   Sitio Web:       http://localhost:5173
echo   API REST:        http://127.0.0.1:8000/api/
echo   Panel de Admin:  http://127.0.0.1:8000/admin/
echo.
echo   MANTEN ESTA VENTANA ABIERTA para que el sistema funcione.
echo   Para salir, presiona Ctrl+C o cierra esta ventana.
echo ===================================================
echo.

start http://localhost:5173
npm run dev

