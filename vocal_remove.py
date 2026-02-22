# vocal_remove.py
import subprocess
import os
import shutil
import torch

MODEL = "mdx_extra_q"
TEMP_DIR = "temp"

def remove_vocals(audio_path, output_path, mode="quality", progress_callback=None):
    """
    Usuwa wokal z piosenki przy użyciu Demucs.
    
    Args:
        audio_path: ścieżka do pliku audio
        output_path: ścieżka do zapisu instrumentu
        mode: "quality" (domyślnie) lub "speed"
              - "quality": shifts=4, segment=24 (lepszy wynik, wolniej)
              - "speed": shifts=1, segment=30 (szybciej, -10% jakości)
        progress_callback: funkcja callback(current, max, text) do aktualizacji progressbaru
    """
    
    # Wykrywanie GPU i GPU memory optimization
    if torch.cuda.is_available():
        device = "cuda"
        # Czyszczenie cache GPU przed przetwarzaniem
        torch.cuda.empty_cache()
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✓ GPU dostępne ({gpu_memory:.1f} GB)")
    else:
        device = "cpu"
        print("⚠ GPU nieznalezione, używam CPU (wolniej)")

    # Parametry zależy od trybu
    if mode == "speed":
        shifts = "1"       # Minimum shifts
        segment = "30"     # Max segment dla CPU/mały GPU
        print(f"⚡ Tryb SPEED: szybsze przetwarzanie")
    else:  # quality (domyślnie)
        shifts = "4"       # 4x lepszej jakości (audio shifts)
        segment = "24"     # Dłuższe segmenty = lepsze kontekst
        print(f"🎯 Tryb QUALITY: wyższa jakość")

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

    print(f"🎧 Uruchamiam Demucs (device: {device}, shifts: {shifts}, segment: {segment})...")
    if progress_callback:
        progress_callback(0, 100, "Demucs: przetwarzanie...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd Demucs: {e}")
        raise

    # Budowanie ścieżki do pliku wynikowego
    track_name = os.path.splitext(os.path.basename(audio_path_fixed))[0]
    src = os.path.join(TEMP_DIR, MODEL, track_name, "no_vocals.wav")

    if not os.path.exists(src):
        raise FileNotFoundError("Nie znaleziono pliku no_vocals.wav po demuksowaniu!")

    # Tworzenie katalogu docelowego jeśli nie istnieje
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Przenoszenie pliku wynikowego
    shutil.move(src, output_path)

    # Czyszczenie GPU cache po przetwarzaniu
    if device == "cuda":
        torch.cuda.empty_cache()

    if progress_callback:
        progress_callback(100, 100, "Demucs: gotowe!")

    print(f"✅ Instrument zapisany: {output_path}")
    return output_path

# --- Przykładowe użycie ---
if __name__ == "__main__":
    # Podmień na swój plik, używając surowego stringa r"ścieżka"
    input_file = r"E:\DOWNLOADS\noweDni.mp3"
    output_file = r"E:\DOWNLOADS\noweDni_no_vocals.wav"
    remove_vocals(input_file, output_file)
