# timing_engine.py
import pygame
import time
import sys
import os

class KaraokeTiming:
    def __init__(self, audio_file, lyrics_file, output_lrc):
        self.audio_file = audio_file
        self.lyrics_file = lyrics_file
        self.output_lrc = output_lrc

        # ===== USTAWIENIA WIDOKU =====
        self.WIDTH = 1000
        self.HEIGHT = 500
        self.FONT_SIZE = 32
        self.LINE_SPACING = 42
        self.LINES_BEFORE = 2
        self.LINES_AFTER = 3

        self.BG = (15, 15, 15)
        self.ACTIVE = (255, 80, 80)
        self.PAST = (160, 160, 160)
        self.FUTURE = (220, 220, 220)

    def load_lyrics(self):
        with open(self.lyrics_file, "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]

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
        pygame.display.set_caption("🎤 Timing – SPACE = następna linia")
        clock = pygame.time.Clock()

        font = pygame.font.SysFont("arial", self.FONT_SIZE)

        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()

        start_time = time.time()
        current = 0
        running = True

        while running:
            clock.tick(60)
            screen.fill(self.BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_SPACE and current < len(lyrics):
                        now = time.time() - start_time
                        timings.append((now, lyrics[current]))
                        current += 1

                        if current >= len(lyrics):
                            running = False

            # ===== RYSOWANIE LINII =====
            center_y = self.HEIGHT // 2
            start = max(0, current - self.LINES_BEFORE)
            end = min(len(lyrics), current + self.LINES_AFTER + 1)

            y = center_y - (current - start) * self.LINE_SPACING

            for i in range(start, end):
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

        # ===== ZAPIS LRC =====
        with open(self.output_lrc, "w", encoding="utf-8") as f:
            for t, line in timings:
                f.write(f"[{self.format_time(t)}]{line}\n")

        print("✅ Timing zapisany:", self.output_lrc)
