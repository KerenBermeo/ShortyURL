import random
import string
from flask import Flask, jsonify, request, render_template, redirect
from db.database import collection



app = Flask(__name__)



BASE_URL = "https://shorty.url/"

@app.route('/')
def home():
    return render_template('index.html')

def generate_short_url():
    characters = string.ascii_letters + string.digits
    id_url = ''.join(random.choices(characters, k=5))
    return id_url

@app.route('/shorten', methods=['POST'])
def shorten_url():
    try:
        # Verificar el tipo de contenido de la solicitud
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        original_url = data.get('url')
        if not original_url:
            return jsonify({"error": "URL is required"}), 400

        # Verificar si la URL ya está en la base de datos
        existing_url = collection.find_one({"original_url": original_url})
        if existing_url:
            return jsonify({"original_url": original_url, "short_url": BASE_URL + existing_url['short_id']}), 200

        # Generar un identificador único de 4 caracteres y verificar si ya existe
        short_id = str
        while True:
            short_id_candidate = generate_short_url()
            existing_short_url = collection.find_one({"short_id": short_id_candidate})
            if not existing_short_url:
                short_id = short_id_candidate
                break

        # Insertar el nuevo short_id en la base de datos
        collection.insert_one({"original_url": original_url, "short_id": short_id})
        

        return jsonify({"original_url": original_url, "short_url": BASE_URL + short_id}), 201
    
    except Exception as e:
        # Imprimir la excepción para depurar
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/<short_id>')
def redirect_url(short_id):
    try:
        # Buscar la URL original usando el short_id
        url_data = collection.find_one({"short_url": short_id})
        if url_data:
            # Redirigir a la URL original
            return redirect(url_data["original_url"])
        else:
            return jsonify({"error": "URL not found"}), 404
    except Exception as e:
        # Manejar errores inesperados
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500
    


if __name__ =='__main__':
    app.run(debug=True)