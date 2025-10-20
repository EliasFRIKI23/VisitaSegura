# Sistema de Gestión de Usuarios - VisitaSegura

## Descripción
Se ha implementado un sistema completo de gestión de usuarios (CRUD) que permite a los administradores crear, leer, actualizar y eliminar usuarios del sistema.

## Características Implementadas

### 1. Vista de Gestión de Usuarios (`core/views/usuarios_view.py`)
- **Tabla de usuarios**: Muestra todos los usuarios con sus datos principales
- **Operaciones CRUD completas**:
  - ➕ **Agregar Usuario**: Crear nuevos usuarios con validación
  - ✏️ **Editar Usuario**: Modificar datos existentes (incluyendo contraseña)
  - 🗑️ **Eliminar Usuario**: Eliminar usuarios con confirmación
  - 🔄 **Actualizar**: Refrescar la lista de usuarios

### 2. Interfaz de Usuario
- **Diseño profesional**: Interfaz moderna con colores institucionales
- **Validación de formularios**: Campos requeridos y validaciones
- **Confirmaciones de seguridad**: Diálogos de confirmación para operaciones críticas
- **Indicadores visuales**: Colores para roles y estados de usuarios

### 3. Seguridad y Permisos
- **Solo administradores**: Acceso restringido a usuarios con rol "admin"
- **Protección de datos**: Contraseñas no se muestran en la tabla
- **Validaciones**: No se puede eliminar el último administrador
- **Verificación de permisos**: Verificación en cada operación

### 4. Integración con el Sistema Principal
- **Botón dinámico**: El botón "👥 Usuarios" solo aparece para administradores
- **Navegación integrada**: Se integra perfectamente con el sistema de navegación
- **Títulos dinámicos**: El título de la ventana cambia según la vista activa

## Cómo Usar el Sistema

### Para Administradores:
1. **Iniciar sesión** con credenciales de administrador (admin/admin123)
2. **Ver el botón "👥 Usuarios"** en el menú principal (solo visible para admins)
3. **Hacer clic en "👥 Usuarios"** para acceder a la gestión
4. **Usar las operaciones CRUD**:
   - Agregar nuevos usuarios
   - Editar usuarios existentes
   - Eliminar usuarios (con restricciones)
   - Actualizar la lista

### Campos de Usuario:
- **Usuario**: Nombre de usuario único
- **Contraseña**: Contraseña del usuario
- **Nombre Completo**: Nombre real del usuario
- **Rol**: admin o guardia
- **Estado**: Activo/Inactivo

## Archivos Modificados/Creados

### Nuevos Archivos:
- `core/views/usuarios_view.py` - Vista principal de gestión de usuarios

### Archivos Modificados:
- `core/views/__init__.py` - Agregada importación de UsuariosView
- `core/main_window.py` - Integración del botón y navegación
- `core/auth_manager.py` - Mejorado método update_user para contraseñas

## Funcionalidades del Sistema CRUD

### CREATE (Crear)
- Formulario de nuevo usuario con validación
- Verificación de nombres de usuario únicos
- Creación automática de usuarios por defecto si no existen

### READ (Leer)
- Tabla con todos los usuarios del sistema
- Información detallada: usuario, nombre, rol, estado, último login
- Colores diferenciados por rol y estado

### UPDATE (Actualizar)
- Edición de todos los campos del usuario
- Actualización de contraseñas opcional
- Campo de usuario bloqueado en modo edición

### DELETE (Eliminar)
- Eliminación con confirmación
- Protección contra eliminación del último administrador
- Validación de permisos antes de eliminar

## Seguridad Implementada

1. **Verificación de roles**: Solo administradores pueden acceder
2. **Validación de formularios**: Campos requeridos y formatos
3. **Confirmaciones**: Diálogos de confirmación para operaciones críticas
4. **Protección de datos**: Contraseñas no visibles en la interfaz
5. **Restricciones de eliminación**: No se puede eliminar el último admin

## Notas Técnicas

- **Base de datos**: Utiliza MongoDB con la colección "Usuarios"
- **Interfaz**: PySide6 con diseño responsivo
- **Validación**: Validación tanto en frontend como backend
- **Navegación**: Integrado con el sistema de navegación existente
- **Temas**: Compatible con modo claro y oscuro

El sistema está completamente funcional y listo para usar. Los administradores pueden gestionar usuarios de manera segura y eficiente.
