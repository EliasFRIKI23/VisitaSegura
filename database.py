# database.py
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
import os
import socket


# URL de conexión a MongoDB Atlas
MONGO_URI = "mongodb+srv://feliaravena_db_user:6FitO8nAmbEgPRlj@visitasegura.m4fpfsy.mongodb.net/miapp?retryWrites=true&w=majority&appName=VisitaSegura"
OFFLINE_ENV_VAR = "VISITASEGURA_OFFLINE"

# Timeout para conexión (5 segundos - suficiente para detectar bloqueos DNS rápidamente)
CONNECTION_TIMEOUT = 5  # segundos

# Crear conexión global
client = None
db = None
usuarios_collection = None
visitantes_collection = None


def _is_offline_mode() -> bool:
    return os.environ.get(OFFLINE_ENV_VAR) == "1"


def connect_db():
    """Inicializa la conexión con MongoDB."""
    global client, db, usuarios_collection, visitantes_collection

    if _is_offline_mode():
        print("⚠️ Modo offline activo: se omite la conexión a MongoDB.")
        client = None
        db = None
        usuarios_collection = None
        visitantes_collection = None
        return False

    try:
        # Configurar timeout para evitar que se quede colgado con DNS bloqueados
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=CONNECTION_TIMEOUT * 1000,  # Convertir a milisegundos
            connectTimeoutMS=CONNECTION_TIMEOUT * 1000,
            socketTimeoutMS=CONNECTION_TIMEOUT * 1000
        )
        
        # Intentar un ping rápido para verificar conectividad
        client.admin.command("ping")
        
        db = client["miapp"]

        # Colecciones
        usuarios_collection = db["Usuarios"]
        visitantes_collection = db["Visitantes"]

        print("Conectado a MongoDB correctamente")
        print(f"Base de datos: {db.name}")
        print(f"Colecciones disponibles: {db.list_collection_names()}")
        return True

    except (ServerSelectionTimeoutError, socket.gaierror, ConfigurationError) as e:
        # Errores de DNS, timeout o configuración (incluye bloqueos de DNS)
        print(f"Error de conexión (posible bloqueo DNS o sin internet): {e}")
        client = None
        db = None
        usuarios_collection = None
        visitantes_collection = None
        return False
    except Exception as e:
        print("Error al conectar con MongoDB:", e)
        client = None
        db = None
        usuarios_collection = None
        visitantes_collection = None
        return False


def check_connection():
    """Verifica si la conexión con MongoDB sigue activa."""
    if _is_offline_mode():
        print("Modo offline: verificación de conexión omitida.")
        return False
    try:
        if client:
            client.admin.command("ping")
            print("Conexion con MongoDB verificada correctamente")
            return True
        else:
            print("Cliente no inicializado. Llama a connect_db() primero.")
            return False
    except Exception as e:
        print("Error al verificar la conexion con MongoDB:", e)
        return False


def get_visitantes_collection():
    """Retorna la colección de visitantes"""
    if _is_offline_mode():
        return None
    if visitantes_collection is None:
        connect_db()
    return visitantes_collection


def get_db():
    """Retorna la instancia de la base de datos"""
    if _is_offline_mode():
        return None
    if db is None:
        connect_db()
    return db
