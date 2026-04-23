@echo off
title Sistema PyME Chile
echo ====================================
echo   Sistema PyME Chile - Iniciando...
echo ====================================
cd /d "%~dp0"

echo Verificando Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop no está en ejecución.
    echo Por favor abre Docker Desktop y vuelve a intentarlo.
    pause
    exit /b 1
)

echo Iniciando servicios...
docker compose up -d --build

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Sistema iniciado correctamente!
    echo.
    echo Accede desde: http://localhost
    echo Usuario:      admin
    echo Contraseña:   admin1234
    echo ====================================
    timeout /t 3 /nobreak >nul
    start http://localhost
) else (
    echo ERROR: No se pudo iniciar el sistema.
    pause
)
