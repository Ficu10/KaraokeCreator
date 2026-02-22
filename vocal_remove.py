# vocal_remove.py
import subprocess
import os
import shutil
import torch

MODEL = "mdx_extra_q"
TEMP_DIR = "temp"

def remove_vocals(audio_path, output_path):
    # Wykrywanie GPU
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(f"Wykorzystywane urządzenie: {device}")

    # Parametry przyspieszające, bez ryzyka OOM na 4GB GPU
    shifts = "1"    # minimalna liczba shiftów → szybciej
    segment = "10"  # krótkie segmenty, mniej VRAM

    # Używamy raw string lub podwójnych backslashy w ścieżce, żeby Windows nie psuł demucsa
    audio_path_fixed = os.path.abspath(audio_path)

    cmd = [
        "demucs",
        "-n", MODEL,
        "--two-stems", "vocals",
        "--shifts", shifts,
        "--segment", segment,
        audio_path_fixed,
        "-o", TEMP_DIR,
        "--device", device
    ]

    print("Uruchamiam Demucs...")
    subprocess.run(cmd, check=True)

    # Budowanie ścieżki do pliku wynikowego
    track_name = os.path.splitext(os.path.basename(audio_path_fixed))[0]
    src = os.path.join(TEMP_DIR, MODEL, track_name, "no_vocals.wav")

    if not os.path.exists(src):
        raise FileNotFoundError("Nie znaleziono pliku no_vocals.wav po demuksowaniu!")

    # Tworzenie katalogu docelowego jeśli nie istnieje
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Przenoszenie pliku wynikowego
    shutil.move(src, output_path)

    print(f"Plik instrumentalny zapisany jako: {output_path}")
    return output_path

# --- Przykładowe użycie ---
if __name__ == "__main__":
    # Podmień na swój plik, używając surowego stringa r"ścieżka"
    input_file = r"E:\DOWNLOADS\noweDni.mp3"
    output_file = r"E:\DOWNLOADS\noweDni_no_vocals.wav"
    remove_vocals(input_file, output_file)
