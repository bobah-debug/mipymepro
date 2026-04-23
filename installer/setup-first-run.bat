@echo off
title Sistema PyME Chile - Configuración Inicial
echo ====================================
echo   Configuración inicial del sistema
echo ====================================
cd /d "%~dp0"

echo Construyendo imágenes Docker (puede tomar varios minutos la primera vez)...
docker compose build

if %errorlevel% neq 0 (
    echo ERROR al construir. Revisa que Docker Desktop esté corriendo.
    pause
    exit /b 1
)

echo Iniciando base de datos y backend...
docker compose up -d db
timeout /t 10 /nobreak >nul
docker compose up -d backend
timeout /t 5 /nobreak >nul

echo Iniciando frontend...
docker compose up -d frontend

echo.
echo ====================================
echo Configuración completada!
echo El sistema estará disponible en:
echo   http://localhost
echo.
echo Usuario inicial: admin
echo Contraseña:      admin1234
echo.
echo IMPORTANTE: Cambia la contraseña del
echo administrador al primer ingreso.
echo ====================================
pause
