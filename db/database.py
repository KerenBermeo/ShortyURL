from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    print(os.getenv("MONGODB_URI"))
    try:
        client = MongoClient(
            os.getenv("MONGODB_URI"),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=3000
        )
        
        # Verificación de conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB")
        
        # Conexión a la base de datos específica
        db = client.get_database()
        if "urls" not in db.list_collection_names():
            db.create_collection("urls")
            db.urls.create_index("short_id", unique=True)
            
        return db.urls
        
    except ConnectionFailure as e:
        print(f"❌ Error de conexión: {e}")
        raise
    except OperationFailure as e:
        print(f"❌ Error de autenticación: {e}")
        raise

# Uso en tu aplicación
collection = get_db_connection()