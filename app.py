from flask import Flask, request, render_template, send_file, jsonify
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Konfiguracja katalogów
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB upload limit

# Tworzenie wymaganych katalogów
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Sprawdzenie czy plik jest odpowiedniego formatu."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(input_file):
    """Konwertuje plik MP3 na WAV za pomocą FFmpeg."""
    output_file = input_file.rsplit('.', 1)[0] + '.wav'
    subprocess.run(["ffmpeg", "-y", "-i", input_file, output_file], check=True)
    return output_file

def remove_vocals_with_demucs(input_audio, output_folder):
    """Usunięcie wokalu za pomocą Demucs i konwersja wyników przy użyciu FFmpeg."""
    try:
        # Konwersja MP3 do WAV, jeśli plik wejściowy to MP3
        if input_audio.endswith('.mp3'):
            input_audio = convert_to_wav(input_audio)

        # Wywołanie Demucs z flagą --mp3, aby zapisać wyniki jako MP3
        demucs_command = [
            "demucs",
            "-n", "mdx",  # Model mdx
            "--two-stems=vocals",
            "--mp3",  # Zapisz wynik bezpośrednio jako MP3
            "-o", output_folder,
            input_audio
        ]
        subprocess.run(demucs_command, check=True)

        # Znalezienie pliku wynikowego
        filename = os.path.splitext(os.path.basename(input_audio))[0]
        demucs_output_folder = os.path.join(output_folder, "mdx", filename)
        vocals_path = os.path.join(demucs_output_folder, "no_vocals.mp3")  # Domyślnie MP3

        # Sprawdzenie, czy plik istnieje
        if not os.path.exists(vocals_path):
            raise FileNotFoundError("Plik wynikowy nie został wygenerowany przez Demucs.")

        # Opcjonalnie: Konwersja na WAV za pomocą FFmpeg
        final_output_path = os.path.join(output_folder, f"{filename}_no_vocals.wav")
        subprocess.run(["ffmpeg", "-y", "-i", vocals_path, final_output_path], check=True)

        return final_output_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Błąd podczas przetwarzania Demucs: {e}")
    except Exception as e:
        raise RuntimeError(f"Wystąpił błąd: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'Nie przesłano pliku'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Nieobsługiwany typ pliku'}), 400

    # Zapisanie pliku tymczasowego
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        file.save(input_path)
        output_path = remove_vocals_with_demucs(input_path, app.config['PROCESSED_FOLDER'])

        # Zwrócenie pliku wynikowego do użytkownika
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Czyszczenie plików tymczasowych
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
