# Módulo de Gestión de Visitantes - VisitaSegura

## Descripción
Sistema CRUD completo para la gestión de visitantes en el establecimiento, desarrollado con PySide6 y **interfaz intuitiva con iconos, tooltips y ayuda integrada**.

## ✨ Características de Interfaz Intuitiva

### 🎯 **Elementos Visuales Mejorados**
- **📱 Iconos descriptivos** en todos los botones y elementos
- **❓ Símbolos de ayuda** con tooltips explicativos
- **🎨 Colores intuitivos** para estados (verde/rojo)
- **📖 Diálogo de ayuda completo** con guías paso a paso
- **💡 Tooltips informativos** en cada elemento de la interfaz

### 🚀 **Experiencia de Usuario Optimizada**
- **Navegación intuitiva** con iconos reconocibles
- **Mensajes descriptivos** con emojis para mejor comprensión
- **Validaciones visuales** con iconos de error y éxito
- **Estadísticas dinámicas** con indicadores visuales
- **Ayuda contextual** disponible en todo momento

## Características Principales

### ✅ Funcionalidades Implementadas

1. **Registro de Visitantes**
   - ID único automático
   - RUT del visitante
   - Nombre completo
   - Fecha y hora de ingreso automática
   - Acompañante (persona que invita)
   - Sector de destino (Financiamiento, CITT, Auditorio)
   - Estado (Dentro/Fuera del establecimiento)

2. **Gestión de Estados**
   - Botón para cambiar estado entre "Dentro" y "Fuera"
   - Doble clic en la tabla para cambio rápido de estado
   - Colores visuales para identificar estados
   - Confirmación visual de cambios de estado

3. **Interfaz de Usuario Intuitiva**
   - 📋 Lista tabular con iconos descriptivos en headers
   - 📝 Formulario completo con grupos organizados y tooltips
   - ⚡ Formulario rápido con validaciones visuales
   - 🔍 Filtros con iconos y etiquetas descriptivas
   - 📊 Estadísticas con indicadores visuales dinámicos
   - 🎯 Menú contextual con iconos y separadores
   - ❓ Botón de ayuda con diálogo completo integrado
   - 💡 Tooltips explicativos en todos los elementos

4. **Operaciones CRUD**
   - ✅ **Create**: Agregar nuevos visitantes
   - ✅ **Read**: Ver lista completa de visitantes
   - ✅ **Update**: Editar información de visitantes existentes
   - ✅ **Delete**: Eliminar visitantes

5. **Almacenamiento**
   - Persistencia en archivo JSON
   - Carga automática al iniciar
   - Guardado automático en cada operación

## Estructura de Archivos

```
core/
├── visitor_model.py      # Modelo de datos y lógica de negocio
├── visitor_form.py       # Formularios con interfaz intuitiva y tooltips
├── visitor_list.py       # Lista principal con iconos y ayuda integrada
├── help_dialog.py        # Diálogo de ayuda completo con pestañas
└── main_window.py        # Ventana principal (modificada)
```

## Uso del Sistema

### 1. Registro Manual de Visitantes

#### Formulario Completo
- Hacer clic en "➕ Nuevo Visitante"
- **📋 Información Personal:**
  - 🆔 RUT (mínimo 8 caracteres) - con botón "?" para ayuda
  - 👤 Nombre completo (mínimo 3 caracteres) - con tooltip explicativo
- **🏢 Información de Visita:**
  - 🤝 Acompañante (mínimo 3 caracteres) - con validación visual
  - 🏢 Sector (seleccionar de la lista) - con iconos descriptivos
- Hacer clic en "💾 Guardar"

#### Formulario Rápido
- Usar el panel derecho "⚡ Registro Rápido"
- Llenar los campos en el formulario compacto con tooltips
- Hacer clic en "🚀 Registrar Rápido"

### 2. Gestión de Estados

#### Cambio de Estado
- **Doble clic** en cualquier fila para cambiar estado
- **Menú contextual** (clic derecho) → "🔄 Cambiar Estado"
- El estado se alterna entre "Dentro" y "Fuera"
- **Mensaje de confirmación** con iconos y estado actual

#### Indicadores Visuales
- 🟢 **Verde claro**: Visitante dentro del establecimiento
- 🔴 **Rosa claro**: Visitante fuera del establecimiento
- **📊 Estadísticas dinámicas** con iconos según cantidad

### 3. Filtros y Búsqueda

#### Filtros Disponibles
- **🔍 Filtrar** con menú desplegable intuitivo:
  - **Todos**: Muestra todos los visitantes
  - **Dentro**: Solo visitantes dentro del establecimiento
  - **Fuera**: Solo visitantes fuera del establecimiento
  - **Financiamiento**: Solo visitantes dirigidos a Financiamiento
  - **CITT**: Solo visitantes dirigidos a CITT
  - **Auditorio**: Solo visitantes dirigidos a Auditorio
- **Tooltip explicativo** en el filtro

### 4. Edición y Eliminación

#### Editar Visitante
- Seleccionar visitante en la tabla
- Hacer clic en "✏️ Editar" (habilitado al seleccionar)
- Modificar los campos necesarios con validaciones
- Hacer clic en "💾 Actualizar"

#### Eliminar Visitante
- Seleccionar visitante en la tabla
- Hacer clic en "🗑️ Eliminar" (habilitado al seleccionar)
- **Confirmación detallada** con información del visitante
- Confirmar la eliminación irreversible

### 5. Estadísticas y Ayuda

#### 📊 Estadísticas en Tiempo Real
El panel derecho muestra estadísticas dinámicas:
- 👥 **Total**: Visitantes registrados en el sistema
- 🟢 **Dentro**: Visitantes actualmente en el establecimiento
- 🔴 **Fuera**: Visitantes que han salido
- 💡 **Actualización automática** cada 30 segundos

#### 📖 Sistema de Ayuda Integrado
- **❓ Botón de ayuda** en la barra superior
- **Diálogo completo** con 4 pestañas:
  - 🚀 **Inicio Rápido**: Guía paso a paso
  - ⚙️ **Funciones**: Descripción detallada de cada función
  - ⌨️ **Atajos**: Teclas y combinaciones útiles
  - 🔧 **Problemas**: Solución de errores comunes
- **💡 Tooltips** en todos los elementos de la interfaz

## Validaciones

### Validaciones de Datos
- **RUT**: Campo obligatorio, mínimo 8 caracteres
- **Nombre**: Campo obligatorio, mínimo 3 caracteres
- **Acompañante**: Campo obligatorio, mínimo 3 caracteres
- **Sector**: Selección obligatoria de la lista
- **RUT único**: No se permiten RUTs duplicados

### Mensajes de Error Mejorados
- **⚠️ Validación visual** de campos vacíos con iconos
- **📏 Validación de longitud** mínima con tooltips
- **🔍 Advertencia de RUT duplicado** con mensaje descriptivo
- **🗑️ Confirmación de eliminación** con detalles del visitante
- **✅ Mensajes de éxito** con iconos y confirmación visual

## Almacenamiento de Datos

### Formato JSON
Los datos se almacenan en `visitors.json` con la siguiente estructura:

```json
[
  {
    "id": "VIS20241201143022123456",
    "rut": "12345678-9",
    "nombre_completo": "Juan Pérez González",
    "fecha_ingreso": "2024-12-01 14:30:22",
    "acompañante": "María Rodríguez",
    "sector": "Financiamiento",
    "estado": "Dentro"
  }
]
```

### Características del Almacenamiento
- **Backup automático**: Cada operación guarda automáticamente
- **Encoding UTF-8**: Soporte completo para caracteres especiales
- **Formato legible**: JSON con indentación para fácil lectura
- **Recuperación**: Carga automática al iniciar la aplicación

## Navegación en la Aplicación Principal

### Acceso al Módulo
1. Ejecutar la aplicación principal
2. En el sidebar, hacer clic en "Visitantes"
3. El módulo se carga automáticamente

### Otras Secciones
- **Visitas**: En desarrollo (placeholder)
- **Zonas**: En desarrollo (placeholder)
- **Reportes**: En desarrollo (placeholder)

## Próximas Funcionalidades

### 🔄 Funcionalidades Pendientes
1. **Escaneo QR**: Integración con códigos QR para registro automático
2. **Reportes**: Generación de reportes de visitantes
3. **Exportación**: Exportar datos a Excel/PDF
4. **Historial**: Mantener historial de visitas anteriores
5. **Notificaciones**: Alertas para visitantes que llevan mucho tiempo

### 🎯 Mejoras Futuras
1. **Base de datos**: Migración de JSON a SQLite/PostgreSQL
2. **Autenticación**: Sistema de usuarios y permisos
3. **API REST**: Interfaz para integración con otros sistemas
4. **Mobile**: Aplicación móvil complementaria

## Ejecución del Demo

Para probar solo el módulo de visitantes:

```bash
python demo_visitors.py
```

Para ejecutar la aplicación completa:

```bash
python Main.py
```

## Requisitos del Sistema

- Python 3.11+
- PySide6
- Los demás requisitos están en `Requisitos.txt.txt`

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contactar al equipo de desarrollo.
