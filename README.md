# 🎤 Karaoke Creator

Profesjonalne narzędzie do tworzenia wideów karaoke z synchronizacją tekstu. Aplikacja automatycznie usuwa wokal z piosenki, synchronizuje tekst i generuje wideo karaoke gotowe do użycia.

## ✨ Funkcje

- **Usuwanie wokalu** - Rozdziela wokal od instrumentu przy użyciu AI (Demucs)
- **Synchronizacja tekstu** - Automatyczne lub manualne dopasowanie tekstu do muzyki
- **Timing słów** - Dokładna synchronizacja poszczególnych słów
- **Generowanie wideo** - Tworzenie profesjonalnych wideów karaoke w MP4
- **GUI intuicyjny** - Interfejs oparty na PyQt5 z obsługą drag-and-drop

## 📋 Wymagania

- Python 3.8+
- GPU (NVIDIA) - opcjonalnie, ale rekomendowane dla szybszego przetwarzania
- Dependencje:
  - PyQt5
  - moviepy
  - pygame
  - numpy
  - torch
  - demucs

## 🚀 Instalacja

```bash
# Klonuj repozytorium
git clone https://github.com/Ficu10/KaraokeCreator.git
cd KaraokeCreator

# Zainstaluj dependencje
pip install -r requirements.txt

# Zainstaluj Demucs (opcjonalnie z GPU support)
pip install demucs
# Dla GPU (CUDA):
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 💾 Użycie

```bash
python app.py
```

### Interfejs GUI

1. **Timing** - Synchronizuj całe linie tekstu do piosenki
2. **Timing słów** - Synchronizuj poszczególne słowa (wymaga linii ze znacznikami czasu)
3. **Usuń wokal** - Rozdziel wokal od instrumentu
4. **Generuj** - Stwórz wideo karaoke z całymi liniami tekstu
5. **Render słów** - Stwórz wideo karaoke z synchronizacją słów

## 📁 Struktura projektu

```
├── app.py                      # Główne GUI aplikacji
├── timing_engine.py            # Synchronizacja tekstu (linie)
├── timing_engine_words.py      # Synchronizacja tekstu (słowa)
├── vocal_remove.py             # Usuwanie wokalu (Demucs)
├── karaoke_render.py           # Generowanie wideo (linie)
├── karaoke_render_words.py     # Generowanie wideo (słowa)
├── auto_timing.py              # Automatyczna synchronizacja
└── outputs/                    # Folder z wynikami
```

## 📝 Format wejściowy

### Plik LRC (standardowy)
```
[00:12.50] Pierwsza linia tekstu
[00:18.30] Druga linia tekstu
[00:25.00] Trzecia linia tekstu
```

### Plik tekstu TXT
```
Pierwsza linia tekstu
Druga linia tekstu
Trzecia linia tekstu
```

## 🎬 Format wyjściowy

- **Wideo karaoke**: MP4 (1280x720, 30 FPS)
- **Format LRC**: Plik .lrc z zeitowaniem
- **Instrument**: WAV bez wokalu

## ⚙️ Konfiguracja

Ustawienia można zmieniać bezpośrednio w kodzie:

- `karaoke_render.py`: Rozdzielczość, rozmiar czcionki, kolory
- `vocal_remove.py`: Model Demucs, parametry GPU
- `app.py`: Ścieżki, rozmiary interfejsu

## 🤖 Silnik synchronizacji

Aplikacja wykorzystuje:
- **Demucs** - separacja wokal/instrument (AI)
- **DTW (Dynamic Time Warping)** - synchronizacja tekstu do dźwięku
- **Librosa** - analiza audio

## 🔧 Troubleshooting

### Błąd CUDA / GPU
```bash
# Jeśli masz problemy z GPU, użyj CPU:
# Zmień w vocal_remove.py: device = "cpu"
```

### Brak wokalu w wynikach
- Spróbuj zmienić model w `vocal_remove.py`
- Upewnij się, że masz wystarczająco VRAM

### Desynchronizacja tekstu
- Zwiększ dokładność w `timing_engine.py`
- Ręcznie popraw czasowe znaczniki w LRC

## 📄 Licencja

MIT License - patrz plik [LICENSE](LICENSE)

## 👤 Autor

Ficu10 - [GitHub](https://github.com/Ficu10)

## 🤝 Contribucje

Wszelkie pull requesty są mile widziane! W przypadku dużych zmian otwórz issue aby przedtem omówić propozycje.

## ⭐ Podziękowania

- Demucs - za separację źródła dźwięku
- MoviePy - za edycję wideo
- PyQt5 - za interfejs graficzny
