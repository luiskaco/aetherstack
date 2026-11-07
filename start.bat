@echo off
set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"
set "BIN=%BASE%\bin"
set "CONF=%BASE%\conf"

echo [AetherStack] Iniciando servicios...

:: 1. MariaDB
tasklist /FI "IMAGENAME eq mariadbd.exe" 2>NUL | find /I "mariadbd.exe" >NUL
if errorlevel 1 (
    start /b "" "%BIN%\mariadb\mariadbd.exe" --defaults-file="%CONF%\my.ini"
    echo  - MariaDB iniciado.
) else (
    echo  - MariaDB ya estaba activo.
)

:: 2. PHP FastCGI
tasklist /FI "IMAGENAME eq php-cgi.exe" 2>NUL | find /I "php-cgi.exe" >NUL
if errorlevel 1 (
    set "PHP_FCGI_MAX_REQUESTS=0"
    start /b "" "%BIN%\php\php-8.4\php-cgi.exe" -b 127.0.0.1:9000 -c "%BIN%\php\php-8.4\php.ini"
    echo  - PHP FastCGI iniciado.
) else (
    echo  - PHP FastCGI ya estaba activo.
)

:: 3. Nginx
tasklist /FI "IMAGENAME eq nginx.exe" 2>NUL | find /I "nginx.exe" >NUL
if errorlevel 1 (
    cd /d "%BIN%\nginx"
    start /b "" "%BIN%\nginx\nginx.exe" -p "%BIN%\nginx"
    cd /d "%BASE%"
    echo  - Nginx iniciado.
) else (
    echo  - Nginx ya estaba activo.
)

echo.
echo [AetherStack] Listo en http://localhost
