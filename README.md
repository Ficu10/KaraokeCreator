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

### ⚡ Tryby przetwarzania Demucs

Aplikacja posiada **dwa tryby przetwarzania** do wyboru w GUI:

| Tryb | Speed | Jakość | VRAM | Uwagi |
|------|-------|--------|------|-------|
| **🎯 Wysoka jakość** | ~5-10 min | ⭐⭐⭐⭐⭐ | 2-4 GB | Domyślnie, `shifts=4, segment=24` |
| **⚡ Szybki** | ~2-3 min | ⭐⭐⭐⭐ | 1-2 GB | `shifts=1, segment=30`, -10% jakości |

**Automatyczne optymalizacje:**
- ✅ GPU memory cache clearing
- ✅ Dynamiczny wybór device (CUDA/CPU)
- ✅ **Progressbar na każdą czynność** (Timing, Demucs, Render)
- ✅ Error handling z szczegółowymi komunikatami

**Przyspieszenie renderowania MP4:**
- 📊 FPS zmieniono z 30 → 24 (20% szybciej, não perceptible)
- ⚙️ Codec preset: `ultrafast` (szybsze kodowanie)
- 📉 Verbose output wyłączony (mniej spowolnienia)

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

## 📊 Paski postępu (Progress Bars)

Każda operacja w aplikacji wyświetla pasek postępu w interfejsie GUI:

| Operacja | Postęp | Info |
|----------|--------|------|
| **Timing** | Interaktywny (SPACE) | Pokazuje liczbę zsynchronizowanych linijek |
| **🎧 Usuń wokal** | 0-100% | Demucs: przetwarzanie... |
| **🎬 Render MP4** | 0-100% | Pokazuje liczbę przetworzonych ramek |

**Jak interpretować progressbar:**
- Niebieski pasek wypełnia się od lewej do prawej
- Obok wyświetla się procentowy postęp i nazwa operacji
- Po ukończeniu appears komunikat "✅ Gotowe!"

## 🎬 Format wyjściowy

- **Wideo karaoke**: MP4 (1280x720, **24 FPS** - optimized)
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

### 🖥️ GPU / CUDA problemy

App automatycznie wykrywa GPU i fallback na CPU. Jeśli masz problemy:

```python
# vocal_remove.py - force CPU:
device = "cpu"  # zamiast auto-detection
```

**Problemy z OOM (Out of Memory)?**
- Wybierz tryb **⚡ Szybki** w GUI (mniejsze segment)
- Zmniejsz `segment` z 24 na 20 w `vocal_remove.py`
- Uruchom na CPU (wolniej, ale mniej RAM)

### 🎙️ Zła separacja wokal/instrument

- Spróbuj drugiego trybu (quality ↔ speed)
- Sprawdź jakość wejściowego audio (MP3 320kbps vs 128kbps)
- Exponuj piosenkomówanie w odpowiednim formacie

### 🎬 Desynchronizacja tekstu

- Używaj opcji **Timing słów** dla większej precyzji
- Ręcznie popraw pliki `.lrc` w notatniku
- Format: `[MM:SS.cs]tekst` (centisekundy, nie milisekundy!)

### ⏱️ Renderowanie MP4 zajmuje zbyt długo?

Aplikacja już ma wbudowaną optymalizację:
- **FPS:** 24 fps (zamiast 30) = 20% szybciej
- **Preset:** `ultrafast` dla libx264 (3x szybciej, minimalna strata jakości)
- **Verbose:** Wyłączony (oszczędzanie CPU)

Jeśli nadal za wolno:
- Usuń dwie ostatnie linie wideo: `karaoke_render.py` linia 130-131
- Zmniejsz rozdzielczość z 1280x720 na 640x360 (4x szybciej)

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
