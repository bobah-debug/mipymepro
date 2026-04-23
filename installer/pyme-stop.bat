@echo off
title Sistema PyME Chile - Detener
cd /d "%~dp0"
echo Deteniendo Sistema PyME Chile...
docker compose down
echo Sistema detenido.
pause
