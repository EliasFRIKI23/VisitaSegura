# 🐳 VisitaSegura - Docker Setup

Este documento explica cómo ejecutar VisitaSegura usando Docker.

## 📋 Prerrequisitos

- Docker Desktop instalado
- Docker Compose (incluido con Docker Desktop)

## 🚀 Inicio Rápido

### Opción 1: Usando Docker Compose (Recomendado)

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build
```

### Opción 2: Usando Docker directamente

```bash
# Construir la imagen
docker build -t visitasegura .

# Ejecutar el contenedor
docker run -p 8000:8000 \
  -e MONGO_URI=mongodb://host.docker.internal:27017/ \
  -v $(pwd)/report:/app/report \
  visitasegura
```

## 🔧 Configuración

### Variables de Entorno

- `MONGO_URI`: URI de conexión a MongoDB (por defecto: `mongodb://localhost:27017/`)
- `PYTHONUNBUFFERED`: Mantiene la salida de Python sin buffer
- `QT_QPA_PLATFORM`: Configuración para Qt en contenedores (`offscreen`)

### Volúmenes

- `./report:/app/report`: Directorio para reportes Excel
- `./data:/app/data`: Directorio para datos de la aplicación

## 📊 Servicios Incluidos

### MongoDB
- **Puerto**: 27017
- **Usuario**: admin
- **Contraseña**: password123
- **Base de datos**: VisitaSegura

### VisitaSegura App
- **Puerto**: 8000
- **Dependencias**: MongoDB

## 🛠️ Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs solo de la aplicación
docker-compose logs -f visitasegura

# Reiniciar solo la aplicación
docker-compose restart visitasegura

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Acceder al contenedor de la aplicación
docker-compose exec visitasegura bash

# Acceder a MongoDB
docker-compose exec mongodb mongosh
```

## 🔍 Solución de Problemas

### Error de conexión a MongoDB
```bash
# Verificar que MongoDB esté ejecutándose
docker-compose ps

# Ver logs de MongoDB
docker-compose logs mongodb
```

### Error de permisos en reportes
```bash
# Asegurar permisos correctos
chmod 755 report/
```

### Problemas con la cámara en Docker
- La aplicación está configurada para funcionar sin interfaz gráfica
- Para desarrollo local, ejecuta fuera de Docker
- Para producción, considera usar un servicio de cámara web separado

## 📁 Estructura de Archivos Docker

```
.
├── dockerfile              # Imagen de la aplicación
├── docker-compose.yml      # Orquestación de servicios
├── docker-entrypoint.sh    # Script de inicio
├── .dockerignore           # Archivos a ignorar en build
└── Requisitos.txt          # Dependencias Python
```

## 🎯 Características del Dockerfile

- **Base**: Python 3.13-slim
- **Dependencias del sistema**: Todas las librerías necesarias para PySide6, OpenCV, PyZbar
- **Optimización**: Cache de capas para builds más rápidos
- **Seguridad**: Usuario no-root, variables de entorno apropiadas

## 📝 Notas de Desarrollo

- El contenedor está configurado para modo `offscreen` de Qt
- Los reportes se guardan en el volumen `./report`
- MongoDB se inicializa automáticamente con la base de datos
- El script de entrada verifica la conexión antes de iniciar la app
