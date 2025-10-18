#!/bin/bash

# Script de inicio para VisitaSegura en Docker
echo "🚀 Iniciando VisitaSegura..."

# Verificar que MongoDB esté disponible
echo "🔍 Verificando conexión a MongoDB..."
python -c "
import os
import sys
from database import connect_db, check_connection

# Configurar URI de MongoDB desde variable de entorno
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
print(f'Conectando a MongoDB: {mongo_uri}')

if connect_db():
    if check_connection():
        print('✅ Conexión a MongoDB exitosa')
    else:
        print('❌ Error verificando conexión a MongoDB')
        sys.exit(1)
else:
    print('❌ No se pudo conectar a MongoDB')
    print('💡 Asegúrate de que MongoDB esté ejecutándose y accesible')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Error de conexión a MongoDB. Saliendo..."
    exit 1
fi

# Crear directorio de reportes si no existe
mkdir -p /app/report

# Iniciar la aplicación
echo "🎯 Iniciando aplicación VisitaSegura..."
python Main.py
