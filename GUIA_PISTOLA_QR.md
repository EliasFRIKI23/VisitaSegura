# 🔫 Guía de Uso: Pistola Escáner QR en VisitaSegura

## 📋 Índice
1. [Introducción](#introducción)
2. [Configuración de la Pistola QR](#configuración-de-la-pistola-qr)
3. [Cómo Usar en VisitaSegura](#cómo-usar-en-visitasegura)
4. [Solución de Problemas](#solución-de-problemas)
5. [Compatibilidad](#compatibilidad)

---

## 🎯 Introducción

VisitaSegura ahora soporta **dos modos de escaneo QR**:
- **📷 Modo Cámara**: Usa la cámara web del computador
- **🔫 Modo Pistola QR**: Usa un lector QR de mano (pistola escáner)

Esta guía te ayudará a configurar y usar correctamente la pistola QR.

---

## ⚙️ Configuración de la Pistola QR

### Paso 1: Conexión Física
1. Conecta la pistola QR al puerto USB de tu computador
2. Espera a que Windows reconozca el dispositivo (normalmente aparece como "HID Keyboard" o "USB Scanner")
3. Si es la primera vez, Windows instalará los drivers automáticamente

### Paso 2: Verificar Modo de Teclado (Keyboard Mode)

La mayoría de las pistolas QR funcionan en **modo teclado (HID)**. Esto significa que:
- ✅ El escáner simula un teclado
- ✅ Los datos escaneados se escriben como si los escribieras a mano
- ✅ Al terminar, presiona "Enter" automáticamente

**Para verificar:**
1. Abre el Bloc de Notas
2. Escanea un código QR con la pistola
3. Si aparece el contenido del QR seguido de un salto de línea → **Está configurada correctamente**

### Paso 3: Configuraciones Recomendadas

Algunas pistolas QR permiten configuración mediante códigos QR especiales. **Configuraciones recomendadas:**

#### ✅ Sufijo (Enter al final)
- **Activar**: Escanea el código QR de "Add CR" o "Suffix: CR" del manual
- **Esto hace que**: La pistola envíe Enter automáticamente después del código

#### ✅ Velocidad de Transmisión
- **Recomendado**: Alta velocidad (Fast/High Speed)
- **Por qué**: Para evitar problemas con QR largos

#### ✅ Formato de Caracteres
- **Recomendado**: UTF-8 o ASCII
- **Por qué**: Para mantener compatibilidad con caracteres especiales

#### ❌ Prefijos
- **Desactivar**: No uses prefijos en la pistola
- **Por qué**: VisitaSegura detecta automáticamente el tipo de QR

---

## 🎮 Cómo Usar en VisitaSegura

### 1. Abrir el Escáner QR

Desde el menú principal:
```
Menú → Escanear QR (o Ctrl+Q)
```

### 2. Seleccionar Modo Pistola QR

En la ventana del escáner:
1. Busca la sección **"⚙️ Método de Escaneo"** en la parte superior
2. Selecciona el botón **"🔫 Pistola QR"**
3. Verás que aparece un campo de entrada grande

### 3. Escanear un Código QR

#### Método Automático (Recomendado):
1. **Haz clic** en el campo de entrada (debe estar resaltado en verde)
2. **Apunta** la pistola al código QR del carnet
3. **Presiona el gatillo** de la pistola
4. **¡Listo!** El sistema procesará automáticamente el código

#### Método Manual (Alternativo):
1. **Haz clic** en el campo de entrada
2. **Escanea** con la pistola
3. **Presiona** el botón "✅ Procesar QR Manualmente"

### 4. Después del Escaneo

El sistema automáticamente:
- ✅ Detectará el tipo de QR (carnet o visitante)
- ✅ Extraerá el RUT del carnet chileno
- ✅ Consultará el nombre en la API (si está disponible)
- ✅ Pre-rellenará el formulario de registro
- ✅ Te mostrará un mensaje de confirmación

**Solo debes:**
1. Completar los campos faltantes (Acompañante, Sector)
2. Presionar "Registrar"

---

## 🔧 Solución de Problemas

### Problema 1: La pistola no escanea
**Síntomas**: No pasa nada al presionar el gatillo

**Soluciones**:
1. ✅ Verifica que el cable USB esté bien conectado
2. ✅ Revisa que la pistola esté encendida (LED encendido)
3. ✅ Prueba en el Bloc de Notas para verificar funcionamiento
4. ✅ Reconecta el cable USB
5. ✅ Reinicia la aplicación VisitaSegura

### Problema 2: Los datos no aparecen completos
**Síntomas**: Solo aparece parte del código QR

**Soluciones**:
1. ✅ Acerca más la pistola al código (5-15 cm es ideal)
2. ✅ Asegúrate de que el QR esté bien iluminado
3. ✅ Mantén la pistola quieta mientras escanea
4. ✅ Verifica que el QR no esté dañado o arrugado

### Problema 3: El sistema no detecta el RUT del carnet
**Síntomas**: No extrae el RUT automáticamente

**Soluciones**:
1. ✅ Verifica que estés escaneando el QR del reverso del carnet
2. ✅ Escanea de nuevo más cerca
3. ✅ Si persiste, usa el **Modo Cámara** como alternativa
4. ✅ Puedes registrar manualmente usando el formulario

### Problema 4: Se procesa automáticamente antes de terminar
**Síntomas**: El QR se procesa con datos incompletos

**Soluciones**:
1. ✅ Esto es raro pero puede pasar con QR muy cortos
2. ✅ El sistema espera 300ms después del último carácter
3. ✅ Si ocurre, escanea de nuevo más cerca para lectura más rápida
4. ✅ Usa el botón "Procesar Manualmente" si prefieres control total

### Problema 5: "Campo Vacío" al procesar
**Síntomas**: Mensaje de error "Por favor, escanee un código QR"

**Soluciones**:
1. ✅ Asegúrate de hacer clic en el campo antes de escanear
2. ✅ El campo debe tener el cursor parpadeando
3. ✅ Verifica que la pistola esté en modo teclado (HID)
4. ✅ Prueba primero en Bloc de Notas

---

## 🔌 Compatibilidad

### Pistolas QR Compatibles

VisitaSegura es compatible con **cualquier pistola QR que funcione en modo teclado (HID)**:

#### ✅ Marcas Probadas:
- Honeywell (Serie Voyager, Xenon)
- Zebra (Serie DS2200, DS4600)
- Datalogic (QuickScan, PowerScan)
- Symbol/Motorola
- NADAMOO
- Tera
- NETUM
- TaoTronics
- Inateck

#### ⚠️ Requisitos:
- Conexión: USB (con cable o inalámbrico con base USB)
- Modo: HID Keyboard (Teclado)
- Sistema Operativo: Windows 10/11
- Drivers: Automáticos (Plug & Play)

#### ❌ No Compatible:
- Pistolas que solo funcionan en modo serie (RS-232)
- Pistolas que requieren software propietario exclusivo
- Pistolas que no emulan teclado

### Sistemas Operativos

- ✅ Windows 10 (64-bit)
- ✅ Windows 11 (64-bit)
- ⚠️ Windows 7/8 (puede funcionar pero no probado)
- ❌ macOS (aplicación no compatible)
- ❌ Linux (aplicación no compatible)

---

## 📊 Ventajas de Usar Pistola QR

### vs. Modo Cámara:

| Característica | Pistola QR | Cámara Web |
|---------------|------------|------------|
| Velocidad de escaneo | ⚡ Instantáneo | 🐌 2-5 segundos |
| Precisión | ✅ 99.9% | ⚠️ 85-95% |
| Rango de lectura | 📏 5-30 cm | 📏 10-20 cm |
| Condiciones de luz | ☀️ Cualquiera | 💡 Requiere buena luz |
| QR dañados | ✅ Bueno | ❌ Difícil |
| Comodidad | 👍 Excelente | 👌 Regular |
| Costo inicial | 💰 $50-200 USD | 💰 $0 (incluido) |

---

## 🎓 Consejos y Mejores Prácticas

### 💡 Consejos Generales:
1. **Distancia óptima**: 10-15 cm del código QR
2. **Ángulo**: Perpendicular al QR (90 grados)
3. **Iluminación**: No necesita luz especial, pero evita reflejos
4. **Limpieza**: Limpia el lente del escáner regularmente
5. **Tamaño del QR**: Mínimo 2x2 cm recomendado

### ⚡ Para Mayor Velocidad:
1. Mantén el campo de entrada siempre con foco
2. Escanea varios carnets seguidos sin cerrar la ventana
3. El sistema limpia automáticamente el campo después de cada escaneo
4. Usa atajos de teclado: `Ctrl+Q` para abrir escáner

### 🔒 Seguridad:
1. Verifica siempre los datos extraídos antes de confirmar
2. Si el nombre no coincide con el RUT, corrígelo manualmente
3. El sistema muestra logs de debugging en consola para auditoría

---

## 📞 Soporte

Si encuentras problemas no mencionados aquí:

1. **Revisa los logs**: Los mensajes "DEBUG: Pistola QR -" en consola te darán pistas
2. **Prueba primero en Bloc de Notas**: Para descartar problemas de hardware
3. **Verifica la configuración de la pistola**: Consulta el manual del fabricante
4. **Usa el Modo Cámara**: Como alternativa temporal

---

## 📝 Notas Técnicas

### Funcionamiento Interno:
- **Detección**: El campo de texto detecta cambios cada 50ms
- **Auto-procesamiento**: Después de 300ms sin cambios, procesa automáticamente
- **Procesamiento manual**: También soporta Enter y botón manual
- **Validación**: Verifica longitud mínima (10 caracteres) antes de procesar
- **Logs**: Todo el proceso se registra en consola para debugging

### Formatos de QR Soportados:
- ✅ QR de carnets chilenos (URL Registro Civil)
- ✅ QR con datos de RUT en texto plano
- ✅ QR de visitantes (formato JSON)
- ✅ QR genéricos (se muestra contenido)

---

## ✅ Checklist de Verificación

Antes de usar la pistola QR en producción, verifica:

- [ ] La pistola escanea correctamente en Bloc de Notas
- [ ] Los datos aparecen seguidos de Enter automático
- [ ] El modo "Pistola QR" está seleccionado en VisitaSegura
- [ ] El campo de entrada tiene el foco (cursor visible)
- [ ] Probaste con al menos 3 carnets diferentes
- [ ] El RUT se extrae correctamente del QR
- [ ] El formulario se pre-rellena con los datos
- [ ] Puedes completar un registro completo sin errores

---

## 🎉 ¡Listo para Usar!

Si completaste el checklist anterior, estás listo para usar la pistola QR en producción. 

**¡Feliz escaneo!** 🚀

---

*Última actualización: Octubre 2024*
*VisitaSegura v2.0*

