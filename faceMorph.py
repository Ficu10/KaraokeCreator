import subprocess
import os
import time
import torch
import librosa
import shutil

MODEL = "mdx_extra_q"
TEMP_DIR = "temp_benchmark"

def benchmark_demucs(audio_path, duration_sec=10):
    # Wykrywanie GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Wykorzystywane urządzenie: {device}")

    # Parametry przyspieszające
    shifts = "1"
    segment = "10"

    # Tworzymy folder tymczasowy
    os.makedirs(TEMP_DIR, exist_ok=True)

    start_time = time.time()

    cmd = [
        "demucs",
        "-n", MODEL,
        "--two-stems", "vocals",
        "--shifts", shifts,
        "--segment", segment,
        audio_path,
        "-o", TEMP_DIR,
        "--device", device  # <- wymuszenie GPU
    ]

    subprocess.run(cmd, check=True)

    elapsed = time.time() - start_time

    # Czyszczenie wyników benchmarku
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f"Czas przetworzenia fragmentu {duration_sec}s: {elapsed:.2f} sekund")

    # Szacunkowy czas dla całego utworu
    y, sr = librosa.load(audio_path, sr=None)
    total_duration = len(y) / sr
    estimated_total = elapsed * (total_duration / duration_sec)
    print(f"Przybliżony czas przetworzenia całego utworu ({int(total_duration)}s): {estimated_total:.2f} sekund")

    return elapsed, estimated_total

# --- Przykładowe użycie ---
if __name__ == "__main__":
    test_file = r"E:\DOWNLOADS\noweDni.mp3"  # Podmień na swój plik
    benchmark_demucs(test_file)
