@echo off
set "BASE=D:\LabIA\aetherstack"
set "BIN=%BASE%\bin"
set "CONF=%BASE%\conf"

echo [AetherStack] Deteniendo servicios...

cd /d "%BIN%\nginx" 2>NUL
nginx.exe -s stop -p "%BIN%\nginx" 2>NUL
cd /d "%BASE%" 2>NUL

taskkill /F /IM nginx.exe /T 2>NUL
taskkill /F /IM php-cgi.exe /T 2>NUL
taskkill /F /IM mariadbd.exe /T 2>NUL
taskkill /F /IM mysqld.exe /T 2>NUL

echo [AetherStack] Todos los servicios detenidos limpiamente.
