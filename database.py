# database.py
from pymongo import MongoClient
import os


# Leer URI desde .env o usar local por defecto
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Crear conexión global
client = None
db = None
usuarios_collection = None
visitantes_collection = None


def connect_db():
    """Inicializa la conexión con MongoDB."""
    global client, db, usuarios_collection, visitantes_collection

    try:
        client = MongoClient(MONGO_URI)
        db = client["VisitaSegura"]

        # Colecciones
        usuarios_collection = db["Usuarios"]
        visitantes_collection = db["Visitantes"]

        print("Conectado a MongoDB correctamente")
        print(f"Base de datos: {db.name}")
        print(f"Colecciones disponibles: {db.list_collection_names()}")
        return True

    except Exception as e:
        print("Error al conectar con MongoDB:", e)
        return False


def check_connection():
    """Verifica si la conexión con MongoDB sigue activa."""
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
    if visitantes_collection is None:
        connect_db()
    return visitantes_collection


def get_db():
    """Retorna la instancia de la base de datos"""
    if db is None:
        connect_db()
    return db
