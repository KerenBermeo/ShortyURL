from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

# Configurar la conexión a MongoDB
mongodb_uri = os.getenv('MONGODB_URI').strip('"')
client = MongoClient(mongodb_uri)
db = client["url_shortener"]
collection = db["urls"]
