from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

# Configurar la conexión a MongoDB
mongodb_uri = os.getenv('MONGODB_URI').strip('"')
client = MongoClient(mongodb_uri)
db = client["url_shortener"]
collection = db["urls"]


# Verificar la conexión consultando una colección
try:
    # Intentar contar documentos en la colección
    count = collection.count_documents({})
    print(f"Conexión exitosa a MongoDB.")
except Exception as e:
    print("Error al conectar a la colección 'urls' en MongoDB:", e)