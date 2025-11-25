@echo off
REM Script para generar el ejecutable de VisitaSegura
REM Este script automatiza el proceso de construcción del EXE

echo ==========================================
echo   Generando VisitaSegura.exe
echo ==========================================
echo.

REM Paso 1: Convertir icono a ICO
echo [1/3] Convirtiendo icono a formato ICO...
python convert_icon_to_ico.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo convertir el icono
    pause
    exit /b 1
)
echo.

REM Paso 2: Limpiar builds anteriores
echo [2/3] Limpiando builds anteriores...
if exist build (
    rmdir /s /q build
    echo Build anterior eliminado
)
if exist dist (
    rmdir /s /q dist
    echo Dist anterior eliminado
)
echo.

REM Paso 3: Generar el ejecutable
echo [3/3] Generando ejecutable con PyInstaller...
pyinstaller --clean Main.spec
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo generar el ejecutable
    pause
    exit /b 1
)
echo.

echo ==========================================
echo   ¡Ejecutable generado exitosamente!
echo ==========================================
echo.
echo El archivo se encuentra en: dist\VisitaSegura.exe
echo.
pause

