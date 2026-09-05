@echo off
title FUNCREES Legacy SPA
cd /d \ %~dp0\
echo Iniciando SPA Clasica en http://localhost:5500...
start http://localhost:5500
npx serve . -p 5500 --no-clipboard
