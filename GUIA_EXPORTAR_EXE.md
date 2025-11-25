# 📦 Guía para Exportar VisitaSegura a EXE

Esta guía te ayudará a generar el archivo ejecutable `.exe` de VisitaSegura con todos los recursos necesarios, incluyendo el icono personalizado.

## 📋 Requisitos Previos

1. ✅ Python instalado (versión 3.8 o superior)
2. ✅ Todas las dependencias instaladas (`pip install -r Requisitos.txt`)
3. ✅ PyInstaller instalado (`pip install pyinstaller`)
4. ✅ Pillow instalado para convertir iconos (`pip install pillow`)

## 🎯 Pasos para Exportar a EXE

### Paso 1: Preparar el Icono del Ejecutable

El icono del EXE debe estar en formato `.ico`. Si solo tienes `Main_logo.png`, conviértelo:

```bash
python convert_icon_to_ico.py
```

Este script:
- Convierte `core/ui/icons/Main_logo.png` a `core/ui/icons/Main_logo.ico`
- Crea múltiples tamaños del icono (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- Asegura que el icono funcione correctamente en Windows

**Nota:** Si prefieres convertir manualmente, puedes usar herramientas online como:
- https://convertio.co/png-ico/
- https://www.icoconverter.com/

### Paso 2: Verificar Recursos Necesarios

Asegúrate de que existan estos archivos en tu proyecto:

```
VisitaSegura/
├── Main.py                          ✅ Archivo principal
├── Main.spec                        ✅ Configuración de PyInstaller
├── Logo Duoc .png                  ✅ Logo de la aplicación
├── core/
│   ├── ui/
│   │   └── icons/
│   │       ├── Main_logo.png       ✅ Icono PNG
│   │       ├── Main_logo.ico       ✅ Icono ICO (generado en Paso 1)
│   │       └── [todos los iconos]  ✅ Todos los iconos PNG
│   └── [resto de módulos]          ✅ Todos los módulos del core
└── database.py                      ✅ Configuración de BD
```

### Paso 3: Revisar el Archivo Main.spec

El archivo `Main.spec` ya está configurado para:
- ✅ Incluir todos los iconos de `core/ui/icons/`
- ✅ Incluir el logo `Logo Duoc .png`
- ✅ Incluir las DLLs necesarias de OpenCV y PyZbar
- ✅ Configurar el icono del ejecutable
- ✅ Incluir todos los módulos ocultos necesarios

**No necesitas modificar nada** a menos que quieras personalizar algo específico.

### Paso 4: Limpiar Builds Anteriores (Opcional)

Si has generado EXEs anteriormente, puedes limpiar los archivos temporales:

```bash
# Eliminar carpeta build (archivos temporales)
rmdir /s /q build

# Eliminar carpeta dist (ejecutables anteriores)
rmdir /s /q dist

# O usar PowerShell:
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

### Paso 5: Generar el Ejecutable

Desde la raíz del proyecto (`E:\Proyecto_Titulo\VisitaSegura`), ejecuta:

```bash
pyinstaller Main.spec
```

O si prefieres más control:

```bash
pyinstaller --clean Main.spec
```

El flag `--clean` limpia los archivos temporales antes de generar.

### Paso 6: Verificar el Ejecutable Generado

Una vez terminado el proceso, encontrarás el ejecutable en:

```
dist/
└── VisitaSegura.exe
```

**Verificaciones:**
1. ✅ El archivo `VisitaSegura.exe` existe en `dist/`
2. ✅ El icono del EXE es `Main_logo` (ver en el explorador de Windows)
3. ✅ El tamaño del archivo es razonable (probablemente entre 50-150 MB)

### Paso 7: Probar el Ejecutable

1. Navega a la carpeta `dist/`
2. Ejecuta `VisitaSegura.exe`
3. Verifica que:
   - ✅ La aplicación se inicia correctamente
   - ✅ Todos los iconos se muestran
   - ✅ El logo de Duoc aparece
   - ✅ La funcionalidad QR funciona (si está disponible)
   - ✅ La conexión a MongoDB funciona (o el modo offline)

## 🔧 Solución de Problemas

### Problema: "No module named 'xxx'"

**Solución:** Agrega el módulo faltante a `hiddenimports` en `Main.spec`:

```python
hiddenimports=[
    # ... módulos existentes ...
    'nombre_del_modulo_faltante',  # Agregar aquí
],
```

Luego regenera el EXE.

### Problema: Los iconos no aparecen en el EXE

**Solución:** 
1. Verifica que `Main_logo.ico` existe en `core/ui/icons/`
2. Verifica que el icono tiene el formato correcto (múltiples tamaños)
3. Regenera con `--clean`: `pyinstaller --clean Main.spec`

### Problema: El EXE es muy grande

**Solución:** Puedes optimizar excluyendo módulos no usados. Edita `Main.spec` y agrega a `excludes`:

```python
excludes=[
    'matplotlib.tests',
    'pandas.tests',
    'numpy.tests',
    # Agregar más módulos de prueba si es necesario
],
```

### Problema: El EXE no encuentra los recursos (iconos, logo)

**Solución:** Asegúrate de que todos los recursos estén incluidos en `datas_to_add` en `Main.spec`. El archivo ya está configurado, pero verifica que las rutas sean correctas.

### Problema: Error al ejecutar: "Failed to execute script"

**Solución:** 
1. Genera el EXE con consola para ver errores:
   ```python
   console=True,  # En lugar de console=False en Main.spec
   ```
2. Ejecuta el EXE desde la terminal para ver los errores
3. Corrige los errores y vuelve a poner `console=False`

## 📝 Comandos Rápidos

### Generación Completa (Recomendado)

```bash
# 1. Convertir icono
python convert_icon_to_ico.py

# 2. Limpiar y generar
pyinstaller --clean Main.spec

# 3. El EXE estará en dist/VisitaSegura.exe
```

### Generación Rápida (sin limpiar)

```bash
pyinstaller Main.spec
```

## 📦 Distribuir la Aplicación

Para distribuir el ejecutable:

1. **Solo el EXE:** Copia `dist/VisitaSegura.exe` a otra máquina
   - ⚠️ Nota: La primera vez puede tardar en iniciar mientras extrae archivos temporales

2. **EXE con dependencias:** Si el EXE no funciona solo, también copia la carpeta completa `dist/`

3. **Requisitos del sistema:**
   - Windows 10 o superior
   - No requiere Python instalado (está incluido en el EXE)
   - No requiere dependencias adicionales (están incluidas)

## ✅ Checklist Final

Antes de considerar el EXE listo:

- [ ] El icono del EXE es correcto (Main_logo)
- [ ] La aplicación se inicia sin errores
- [ ] Todos los iconos se muestran correctamente
- [ ] El logo de Duoc aparece
- [ ] La funcionalidad de QR funciona
- [ ] La conexión a MongoDB funciona (o modo offline)
- [ ] Los reportes se generan correctamente
- [ ] El tamaño del EXE es razonable

## 🎉 ¡Listo!

Tu aplicación `VisitaSegura.exe` está lista para distribuir.

**Ubicación:** `dist/VisitaSegura.exe`

---

**Notas Adicionales:**
- El primer inicio del EXE puede ser más lento mientras se extraen archivos
- Si haces cambios en el código, regenera el EXE con `pyinstaller --clean Main.spec`
- Guarda una copia del `Main.spec` en caso de necesitar modificar la configuración

