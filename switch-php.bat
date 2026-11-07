@echo off
setlocal
set STACK_DIR=%~dp0
set TARGET_VER=%1

if "%TARGET_VER%"=="" (
    echo Uso: switch-php.bat [8.4 ^| 8.5]
    exit /b 1
)

if not exist "%STACK_DIR%bin\php\php-%TARGET_VER%" (
    echo Version php-%TARGET_VER% no encontrada.
    exit /b 1
)

echo Cambiando a PHP %TARGET_VER%...
rmdir "%STACK_DIR%bin\php\current" 2>nul
mklink /J "%STACK_DIR%bin\php\current" "%STACK_DIR%bin\php\php-%TARGET_VER%"
echo Reiniciando FastCGI...
taskkill /F /IM php-cgi.exe 2>nul
start /B "" "%STACK_DIR%bin\php\current\php-cgi.exe" -b 127.0.0.1:9000 -c "%STACK_DIR%bin\php\current\php.ini"
echo PHP %TARGET_VER% activo exitosamente.
