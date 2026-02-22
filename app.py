import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from timing_engine import KaraokeTiming
from timing_engine_words import KaraokeTimingWords      # nowy timing słów
from vocal_remove import remove_vocals
from karaoke_render import render_karaoke
from karaoke_render_words import render_karaoke_words  # nowy render słów

# ================== KONFIG ==================
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ============================================

class KaraokeStudio(QWidget):
    def __init__(self):
        super().__init__()

        # --- Ustawienia okna ---
        self.setWindowTitle("🎤 Karaoke Studio")
        self.setFixedSize(1600, 600)
        self.setStyleSheet("background-color: #742a96;")

        # --- Layout główny ---
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        main_layout.setSpacing(30)

        # --- Nagłówek ---
        header = QLabel("Kreator Karaoke")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 48, QFont.Bold))
        header.setStyleSheet("color: white;")
        main_layout.addWidget(header)

        # --- Przyciski ---
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # stare przyciski
        self.btn_timing = QPushButton("⏱ Timing")
        self.btn_vocals = QPushButton("🎧 Usuń wokal")
        self.btn_render = QPushButton("🎬 Generuj")
        # nowe przyciski słów
        self.btn_timing_words = QPushButton("⏱ Timing słów")
        self.btn_render_words = QPushButton("🎬 Render słów")

        # lista przycisków
        buttons = [
            self.btn_timing,
            self.btn_timing_words,
            self.btn_vocals,
            self.btn_render,
            self.btn_render_words
        ]

        for btn in buttons:
            btn.setFixedSize(220, 120)
            btn.setFont(QFont("Arial", 16, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #b572d4;
                    color: white;
                    border: 3px solid white;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background-color: #c18fe0;
                }
            """)
            buttons_layout.addWidget(btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        # ===== ŚCIEŻKI =====
        self.audio = None
        self.lyrics = None
        self.lrc = os.path.join(OUTPUT_DIR, "lyrics.lrc")
        self.instrumental = os.path.join(OUTPUT_DIR, "instrumental.wav")

        # ===== SYGNAŁY =====
        self.btn_timing.clicked.connect(self.run_timing)
        self.btn_timing_words.clicked.connect(self.run_timing_words)
        self.btn_vocals.clicked.connect(self.run_vocals)
        self.btn_render.clicked.connect(self.run_render)
        self.btn_render_words.clicked.connect(self.run_render_words)

    # ================== TIMING SŁÓW ==================
    def run_timing_words(self):
        self.audio, _ = QFileDialog.getOpenFileName(self, "Wybierz piosenkę", "", "Audio (*.mp3 *.wav)")
        if not self.audio:
            return
        self.lyrics, _ = QFileDialog.getOpenFileName(self, "Wybierz tekst", "", "Tekst (*.txt)")
        if not self.lyrics:
            return

        self.lrc = os.path.join(OUTPUT_DIR, "lyrics_words.lrc")
        try:
            engine = KaraokeTimingWords(
                audio_file=self.audio,
                lyrics_file=self.lyrics,
                output_lrc=self.lrc
            )
            engine.run()
            QMessageBox.information(self, "Gotowe", "✅ Timing słów zakończony\nUtworzono lyrics_words.lrc")
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd TIMING SŁÓW", "❌ Sprawdź konsolę (traceback)")

    # ================== RENDER SŁÓW ==================
    def run_render_words(self):
        if not os.path.exists(self.instrumental):
            QMessageBox.warning(self, "Błąd", "❌ Brak instrumental.wav")
            return
        if not os.path.exists(self.lrc):
            QMessageBox.warning(self, "Błąd", "❌ Brak lyrics_words.lrc")
            return

        song_name = os.path.splitext(os.path.basename(self.audio))[0]
        output_video = os.path.join(OUTPUT_DIR, f"{song_name}_words.mp4")

        try:
            render_karaoke_words(
                instrumental=self.instrumental,
                lrc_file=self.lrc,
                output_mp4=output_video
            )
            QMessageBox.information(self, "Sukces 🎉", f"✅ Karaoke słów zapisane:\n{output_video}")
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd renderowania słów", "❌ Sprawdź konsolę (traceback)")

    # ================== STARE FUNKCJE ==================
    # tutaj pozostają Twoje stare run_timing, run_vocals, run_render, run_auto...


    # ================== TIMING ==================
    def run_timing(self):
        self.audio, _ = QFileDialog.getOpenFileName(self, "Wybierz piosenkę", "", "Audio (*.mp3 *.wav)")
        if not self.audio:
            return

        self.lyrics, _ = QFileDialog.getOpenFileName(self, "Wybierz tekst", "", "Tekst (*.txt)")
        if not self.lyrics:
            return

        print("=== TIMING START ===")
        print("AUDIO:", self.audio)
        print("LYRICS:", self.lyrics)
        print("OUTPUT LRC:", self.lrc)

        try:
            engine = KaraokeTiming(
                audio_file=self.audio,
                lyrics_file=self.lyrics,
                output_lrc=self.lrc
            )
            engine.run()

            QMessageBox.information(self, "Gotowe", "✅ Timing zakończony\nUtworzono lyrics.lrc")
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd TIMINGU", "❌ Sprawdź konsolę (traceback)")

    # ================== NO VOCALS ==================
    def run_vocals(self):
        if not self.audio:
            QMessageBox.warning(self, "Błąd", "❌ Najpierw wykonaj TIMING")
            return

        print("=== DEMUCS START ===")
        print("AUDIO:", self.audio)
        print("OUTPUT WAV:", self.instrumental)

        try:
            remove_vocals(self.audio, self.instrumental)
            QMessageBox.information(self, "Gotowe", "✅ Wokal usunięty\nUtworzono instrumental.wav")
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd DEMUCS", "❌ Sprawdź konsolę (traceback)")

    # ================== RENDER MP4 ==================
    def run_render(self):
        if not os.path.exists(self.instrumental):
            QMessageBox.warning(self, "Błąd", "❌ Brak instrumental.wav")
            return
        if not os.path.exists(self.lrc):
            QMessageBox.warning(self, "Błąd", "❌ Brak lyrics.lrc")
            return

        song_name = os.path.splitext(os.path.basename(self.audio))[0]
        output_video = os.path.join(OUTPUT_DIR, f"{song_name}.mp4")

        print("=== RENDER START ===")
        try:
            render_karaoke(instrumental=self.instrumental, lrc_file=self.lrc, output_mp4=output_video)
            QMessageBox.information(self, "Sukces 🎉", f"✅ Karaoke zapisane:\n{output_video}")
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(self, "Błąd renderowania", "❌ Sprawdź konsolę (traceback)")

# ================== START APP ==================
if __name__ == "__main__":
    print("=== KARAOKE STUDIO START ===")
    app = QApplication(sys.argv)
    studio = KaraokeStudio()
    studio.show()
    sys.exit(app.exec())
