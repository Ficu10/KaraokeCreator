import pygame
import time
import os

class KaraokeTimingWords:
    def __init__(self, audio_file, lyrics_file, output_lrc):
        self.audio_file = audio_file
        self.lyrics_file = lyrics_file
        self.output_lrc = output_lrc

        # ===== USTAWIENIA WIDOKU =====
        self.WIDTH = 1000
        self.HEIGHT = 500
        self.FONT_SIZE = 32
        self.LINE_SPACING = 42
        self.LINES_BEFORE = 5   # ile słów przed aktywnym wyświetlać
        self.LINES_AFTER = 10   # ile słów po aktywnym wyświetlać

        self.BG = (15, 15, 15)
        self.ACTIVE = (255, 80, 80)
        self.PAST = (160, 160, 160)
        self.FUTURE = (220, 220, 220)

    def load_lyrics(self):
        # wczytaj linie i rozdziel na słowa
        lyrics_words = []
        with open(self.lyrics_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    lyrics_words.extend(line.split())
        return lyrics_words

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m:02d}:{s:05.2f}"

    def run(self):
        lyrics = self.load_lyrics()
        timings = []

        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("🎤 Timing słów – SPACE = następne słowo")
        clock = pygame.time.Clock()

        font = pygame.font.SysFont("arial", self.FONT_SIZE)

        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()
        start_time = time.time()

        current = 0
        running = True

        while running and current < len(lyrics):
            clock.tick(60)
            screen.fill(self.BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        now = time.time() - start_time
                        # start i koniec tymczasowo takie same
                        timings.append((now, now, lyrics[current]))
                        current += 1

            # ===== WYŚWIETLANIE SŁÓW Z PRZEWIJANIE =====
            center_y = self.HEIGHT // 2
            start_idx = max(0, current - self.LINES_BEFORE)
            end_idx = min(len(lyrics), current + self.LINES_AFTER + 1)

            y = center_y - (current - start_idx) * self.LINE_SPACING

            for i in range(start_idx, end_idx):
                if i < current:
                    color = self.PAST
                elif i == current:
                    color = self.ACTIVE
                else:
                    color = self.FUTURE

                surf = font.render(lyrics[i], True, color)
                rect = surf.get_rect(center=(self.WIDTH // 2, y))
                screen.blit(surf, rect)
                y += self.LINE_SPACING

            pygame.display.flip()

        pygame.quit()

        # ===== ZAPIS LRC SŁÓW =====
        with open(self.output_lrc, "w", encoding="utf-8") as f:
            for start, end, word in timings:
                f.write(f"[{self.format_time(start)}-{self.format_time(end)}]{word}\n")

        print("✅ Timing słów zapisany:", self.output_lrc)
