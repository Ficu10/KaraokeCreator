from flask import Flask, request, render_template, jsonify, url_for
import os
import subprocess
import uuid
import whisper
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

# Konfiguracja katalogów
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB upload limit

# Tworzenie wymaganych katalogów
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Ładowanie modelu Whisper
model = whisper.load_model("medium")

def allowed_file(filename):
    """Sprawdzenie czy plik jest odpowiedniego formatu."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(input_file):
    """Konwertuje plik MP3 na WAV za pomocą FFmpeg."""
    output_file = input_file.rsplit('.', 1)[0] + '.wav'
    subprocess.run(["ffmpeg", "-y", "-i", input_file, output_file], check=True)
    return output_file

def remove_vocals_with_demucs(input_audio):
    """Usunięcie wokalu za pomocą Demucs."""
    try:
        if input_audio.endswith('.mp3'):
            input_audio = convert_to_wav(input_audio)

        output_folder = app.config['PROCESSED_FOLDER']
        demucs_command = [
            "demucs", "-n", "mdx", "--two-stems=vocals", "--mp3", "-o", output_folder, input_audio
        ]
        subprocess.run(demucs_command, check=True)

        filename = os.path.splitext(os.path.basename(input_audio))[0]
        demucs_output_folder = os.path.join(output_folder, "mdx", filename)
        vocals_path = os.path.join(demucs_output_folder, "no_vocals.mp3")

        final_output_path = os.path.join(output_folder, f"{filename}_no_vocals.mp3")
        shutil.move(vocals_path, final_output_path)
        return final_output_path
    except Exception as e:
        raise RuntimeError(f"Błąd usuwania wokalu: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'Nie przesłano pliku'}), 400

    file = request.files['audio']
    language = request.form.get('language', 'pl')  # Domyślny język to "pl"

    if not allowed_file(file.filename):
        return jsonify({'error': 'Nieobsługiwany typ pliku'}), 400

    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        file.save(input_path)
        transcript = model.transcribe(input_path, language=language, temperature=0.0)['text']
        return jsonify({'transcription': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)


@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Nie przesłano pliku'}), 400

    file = request.files['audio']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Nieobsługiwany typ pliku'}), 400

    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        file.save(input_path)
        processed_audio_path = remove_vocals_with_demucs(input_path)
        audio_url = url_for('static', filename=f'processed/{os.path.basename(processed_audio_path)}')
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
