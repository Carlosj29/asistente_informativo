from flask import Flask, render_template, request, jsonify
import openai
import PyPDF2
import docx
import os
import base64
import pygame
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Configuración inicial
load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa pygame para audio
pygame.mixer.init()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def leer_archivo(ruta):
    if ruta.endswith(".txt"):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    elif ruta.endswith(".docx"):
        doc = docx.Document(ruta)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ruta.endswith(".pdf"):
        with open(ruta, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages])
    else:
        raise ValueError("Formato no soportado")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        contenido = leer_archivo(filepath)
        return jsonify({
            "filename": filename,
            "content": contenido[:500] + "..." if len(contenido) > 500 else contenido
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(filepath)

@app.route('/ask', methods=['POST'])
def ask_assistant():
    data = request.json
    pregunta = data.get('question')
    documento = data.get('document', '')
    
    if not pregunta:
        return jsonify({"error": "Pregunta requerida"}), 400
    
    try:
        respuesta = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente amigable y cercano. Responde de forma breve, interactiva y conversacional, como si estuvieras hablando con un amigo."},
                {"role": "user", "content": f"Documento: {documento}\n\nPregunta: {pregunta}"}
            ],
            temperature=0.7
        ).choices[0].message.content
        
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=respuesta
        )
        
        audio_b64 = base64.b64encode(audio_response.content).decode('utf-8')
        
        return jsonify({
            "response": respuesta,
            "audio": audio_b64
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/saludo', methods=['GET'])
def saludo_inicial():
    saludo_texto = "¡Hola! ¿En qué te ayudo hoy?"
    
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=saludo_texto
    )
    
    audio_b64 = base64.b64encode(audio_response.content).decode('utf-8')
    
    return jsonify({"saludo": saludo_texto, "audio": audio_b64})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
