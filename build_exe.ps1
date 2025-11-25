# Script PowerShell para generar el ejecutable de VisitaSegura
# Este script automatiza el proceso de construcción del EXE

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Generando VisitaSegura.exe" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Convertir icono a ICO
Write-Host "[1/3] Convirtiendo icono a formato ICO..." -ForegroundColor Yellow
python convert_icon_to_ico.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo convertir el icono" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Paso 2: Limpiar builds anteriores
Write-Host "[2/3] Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "Build anterior eliminado" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "Dist anterior eliminado" -ForegroundColor Green
}
Write-Host ""

# Paso 3: Generar el ejecutable
Write-Host "[3/3] Generando ejecutable con PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean Main.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo generar el ejecutable" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ¡Ejecutable generado exitosamente!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "El archivo se encuentra en: dist\VisitaSegura.exe" -ForegroundColor Cyan
Write-Host ""
Read-Host "Presiona Enter para salir"

