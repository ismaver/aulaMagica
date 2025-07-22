#---------------------------------------------------------------------------------------------------
try:
    from openai import OpenAI
    from pydub import AudioSegment
except ImportError:
    pass
import logging
import io
import tempfile
import traceback;
import os
import base64
import openai
import traceback
from io import BytesIO
from flask import Flask, abort, request, jsonify, render_template, send_file, send_from_directory
from gtts import gTTS
from pydub import AudioSegment
from flask_cors import CORS


openai.api_key = os.getenv("OPENAI_API_KEY") 
# Inicialización de la aplicación Flask
app = Flask(
    __name__,
    static_folder='static/angular',      # <-- aquí apuntamos al build de Angular
    template_folder='static/angular'
)
CORS(app, origins=['http://localhost:4200', 'http://localhost:5000'])

# Carpeta donde se guardarán las imágenes generadas
IMAGE_FOLDER = 'static'
LAST_IMAGE_FOLDER = 'last_image'
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(LAST_IMAGE_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    """Sirve la página principal."""
    return render_template('index.html')

@app.route('/imagen-ultima')
def imagen_ultima():
    # Nombre fijo de tu imagen
    filename = 'generated_image.png'
    path = os.path.join("static/", filename)
    if not os.path.exists(path):
        abort(404)
    # Devuelve el fichero tal cual con su tipo mime
    return send_file(path, mimetype='image/png')

@app.route('/generate', methods=['POST'])
def generate_image():
    """
    Genera una imagen a partir de un único prompt.
    Espera un JSON con la forma: {"prompt": "tu texto aquí"}
    """
    data = request.json
    #prompt = data.get('prompt').strip()
    prompt = request.json.get('prompt','')
    logger.info("Generando imagen para niños de entre 4 a 6 años aprendad con lo siguiente: %r", prompt)

    # Validar que exista un prompt
    if not prompt:
        return jsonify({"error": "Debes proporcionar un prompt."}), 400

    try:
        # Construir el prompt agregando el estilo deseado
        prompt_completo = f"En estilo de pixar animation Studios, genera la siguiente imagen que tiene como objetivo enseñar a niños de 4 años: {prompt}"

        # Llamada a la API de OpenAI utilizando el cliente instanciado y el nuevo método `images.generate()`
        result = openai.Image.create(
            model="gpt-image-1",  # Usar el modelo correcto
            prompt=prompt_completo,
            size="1024x1024",
            quality="medium" # se puede usar el auto o low esta para que sea menos costoso
        )

        # Obtener la imagen en base64
        image_base64 = result['data'][0]['b64_json']
        image_bytes = base64.b64decode(image_base64) 
        
        # Guardar la imagen generada localmente
        image_path = os.path.join(IMAGE_FOLDER, 'generated_image.png')
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        # Guardar esta imagen como la última generada
        last_image_path = os.path.join(LAST_IMAGE_FOLDER, 'last_image.png')
        with open(last_image_path, 'wb') as f:
            f.write(image_bytes)
            
        logger.info("Imagen guardada en %s", image_path)
        # Retornar la URL de la imagen generada para mostrarla en la web
        return jsonify({"image_url": "/static/generated_image.png"})

    except Exception as e:
        print("Error en la API de OpenAI:", e)
        return jsonify({"error": "Error en la API de OpenAI", "message": str(e)}), 500

@app.route('/api/last-image', methods=['GET'])
def get_last_image():
    """
    Devuelve JSON con la URL de la última imagen generada.
    """
    # La URL viaja siempre bajo /last_image/…
    return jsonify({ "url": "/last_image/last_image.png" })


@app.route('/questions', methods=['POST'])    
def generate_questions():
    """
    Genera 3 preguntas sencillas sobre el prompt o la imagen.
    Espera JSON: { "prompt": "texto" }
    Devuelve: { "questions": [ "¿Pregunta 1?", "¿Pregunta 2?", ... ] }
    """
    
    data = request.json or {}
    prompt_imagen  = data.get('prompt', '').strip()
    if not prompt_imagen :
        return jsonify({"error": "Debes proporcionar un prompt para las preguntas."}), 400

    try:
        system = {
            "role": "system",
            "content": "Eres un maestro para niños de 4 a 6 años. "
        }
        user = {
            "role": "user",
            "content": (
                f"Sin ningún texto adicional, solo devuelve una lista numerada del 1 al 3 de preguntas muy sencillas y claras para un niño de 4-6 años En español "
                f"sobre la siguiente imagen (archivo last_image/last_image.png) "
                f"y la descripción: {prompt_imagen}"
            )
        }
        resp = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[system, user],
            temperature=0.7
        )
        text = resp.choices[0].message.content
        
        # Extraer solo las preguntas (por ejemplo líneas que empiecen con número)
        lines = text.splitlines()
        questions = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # Quitar numeración o guiones
                question = line.lstrip('0123456789.- )')
                questions.append(question.strip())

        if not questions:
            # Si no encontró preguntas con numeración, usar todo el texto como 1 sola pregunta
            questions = [text.strip()]
            
        # Separar líneas y filtrar vacíos
        questions = [q.strip(" -") for q in text.splitlines() if q.strip()]
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": "Error generando preguntas", "message": str(e)}), 500

   
    
@app.route('/tts', methods=['POST'])
def synthesize_tts():
    """
    Convierte texto a voz usando gTTS.
    Espera JSON: { "text": "texto a pronunciar" }
    Devuelve: audio/mpeg
    """
    try:
        # Forzamos parseo del JSON y extraemos texto
        data = request.get_json(force=True)
        text = data.get('text', '').strip()
        print("🔊 TTS request for text:", repr(text))

        if not text:
            print("❌ TTS aborted: texto vacío")
            return jsonify({"error": "Falta el texto para TTS"}), 400

        # Generamos el audio
        tts = gTTS(text=text, lang='es')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return send_file(mp3_fp, mimetype="audio/mpeg")

    except Exception as e:
        # Esto imprimirá el stacktrace completo en tu consola de Flask
        traceback.print_exc()
        return jsonify({"error": "Error en TTS", "message": str(e)}), 500


@app.route('/stt', methods=['POST'])
def synthesize_stt():
    """
    Convierte audio a texto usando Whisper.
    Espera multipart/form-data con 'audio' (archivo).
    Devuelve: { "text": "transcripción" }
    """
    audio_file  = request.files.get('audio')
    if not audio_file :
        return jsonify({"error": "Falta archivo de audio"}), 400

    try:
        # 1) Leemos el blob webm
        webm_bytes = audio_file.read()
        audio_file.seek(0)
        # 2) Convertimos a WAV con pydub
        wav_io = io.BytesIO()
        AudioSegment.from_file(io.BytesIO(webm_bytes), format="webm") \
                    .export(wav_io, format="wav")
        wav_io.seek(0)

        # 3) Pasamos el WAV a Whisper
        
        wav_io.name = "audio.wav"
        
        transcript = openai.Audio.transcribe("whisper-1", wav_io)
        return jsonify({"text": transcript["text"]})
    except Exception as e:
        # log completo para depurar
        traceback.print_exc()
        return jsonify({"error": "Error en STT", "message": str(e)}), 500
    
    
@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Evalúa la respuesta transcrita respecto a la pregunta actual.
    Espera JSON: { "question": "¿...?", "answer": "texto del niño" }
    Devuelve: { "feedback": "Muy bien, ..." }
    """
    data = request.json or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    
    if not question:
        return jsonify({"error":"Falta pregunta"}), 400
    
    system = {
      "role":"system",
      "content": (
        "Eres un tutor experto en pedagogía infantil (4-6 años). "
        "Siempre refuerzas lo que el niño hizo bien, corriges suavemente los errores "
        "y ofreces una pequeña pista para mejorar. Usa un tono alegre y motivador."
      )
    }
    user = {
      "role":"user",
      "content": (
        f"Imagen: last_image.png\n"
        f"Descripción (prompt): {data.get('prompt','')}\n"
        f"Pregunta: {question}\n"
        f"Respuesta: {answer or '[sin respuesta]'}\n\n"
        "Evalúa la respuesta, primero di “¡Muy bien!” si es correcta, "
        "o “Buen intento, pero… ” si falta algo, y da una pista corta."
      )
    }

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[system, user],
            temperature=0.5
        )
        feedback = resp.choices[0].message.content.strip()
        return jsonify({ "feedback": feedback })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error":"Error en evaluación","message":str(e)}),500

@app.route('/healthz')
def healthz():
    return jsonify(status='ok'), 200

# Catch-all SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# # Asegúrate también de servir el service worker:
# @app.route('/ngsw-worker.js')
# def service_worker():
#     return send_from_directory(os.path.join(app.static_folder, 'angular'),
#                                'ngsw-worker.js')

if __name__ == '__main__':
    app.run(debug=True)
