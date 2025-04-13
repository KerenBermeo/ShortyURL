import os
import random
import string
import requests
from datetime import datetime 
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, redirect
from functools import wraps
from db.database import collection

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuración desde variables de entorno
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000/').rstrip('/') + '/'
API_KEYS = os.getenv('API_KEYS', '').split(',')  # Lista de API keys válidas

def validate_url(url):
    """Valida que la URL sea accesible."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        if not all([url.startswith(('http://', 'https://'))]):
            return False, "Invalid URL format"
            
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code < 400, f"HTTP status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def generate_short_url(length=5):
    """Genera un identificador corto aleatorio."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def require_api_key(f):
    """Decorador para proteger endpoints con API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEYS and API_KEYS[0]:
            api_key = request.headers.get('X-API-KEY') or request.args.get('api_key')
            if not api_key or api_key not in API_KEYS:
                return jsonify({"error": "Invalid or missing API key"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """Endpoint principal que muestra la interfaz."""
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
@require_api_key
def shorten_url():
    """
    Acorta una URL recibida en formato JSON.
    """
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    original_url = data.get('url')
    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    is_valid, message = validate_url(original_url)
    if not is_valid:
        return jsonify({"error": f"URL validation failed: {message}"}), 400

    existing_url = collection.find_one({"original_url": original_url})
    if existing_url:
        return jsonify({
            "original_url": original_url,
            "short_url": f"{BASE_URL}{existing_url['short_id']}",
            "stats": {
                "created_at": existing_url["created_at"],
                "last_accessed": existing_url.get("last_accessed"),
                "clicks": existing_url["clicks"]
            }
        }), 200

    short_id = None
    attempts = 0
    max_attempts = 10
    
    while attempts < max_attempts:
        short_id_candidate = generate_short_url()
        if not collection.find_one({"short_id": short_id_candidate}):
            short_id = short_id_candidate
            break
        attempts += 1

    if not short_id:
        return jsonify({"error": "Could not generate a unique short ID"}), 500

    new_url = {
        "original_url": original_url,
        "short_id": short_id,
        "short_url": f"{BASE_URL}{short_id}",
        "created_at": datetime.utcnow(),
        "last_accessed": None,
        "clicks": 0,
        "access_logs": [],
        "metadata": {
            "ip": request.remote_addr,
            "user_agent": request.user_agent.string
        }
    }
    
    collection.insert_one(new_url)

    return jsonify({
        "original_url": original_url,
        "short_url": new_url["short_url"],
        "stats": {
            "created_at": new_url["created_at"],
            "last_accessed": new_url["last_accessed"],
            "clicks": new_url["clicks"]
        }
    }), 201

@app.route('/<short_id>')
def redirect_to_url(short_id):
    """Redirige a la URL original basada en el short_id."""
    url_data = collection.find_one({"short_id": short_id})
    if not url_data:
        return jsonify({"error": "URL not found"}), 404
    
    now = datetime.utcnow()
    access_log = {
        "timestamp": now,
        "ip": request.remote_addr,
        "user_agent": request.user_agent.string
    }
    
    collection.update_one(
        {"short_id": short_id},
        {
            "$set": {"last_accessed": now},
            "$inc": {"clicks": 1},
            "$push": {"access_logs": access_log}
        }
    )
    
    return redirect(url_data["original_url"])

@app.route('/stats/<short_id>', methods=['GET'])
@require_api_key
def url_stats(short_id):
    """Obtiene estadísticas de una URL acortada."""
    url_data = collection.find_one({"short_id": short_id}, {
        "original_url": 1,
        "short_url": 1,
        "created_at": 1,
        "last_accessed": 1,
        "clicks": 1,
        "access_logs": {"$slice": -10}
    })
    
    if not url_data:
        return jsonify({"error": "URL not found"}), 404
    
    return jsonify({
        "original_url": url_data["original_url"],
        "short_url": url_data["short_url"],
        "stats": {
            "created_at": url_data["created_at"],
            "last_accessed": url_data.get("last_accessed"),
            "total_clicks": url_data["clicks"],
            "recent_accesses": url_data.get("access_logs", [])
        }
    }), 200

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_ENV') == 'development',
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000))
    )