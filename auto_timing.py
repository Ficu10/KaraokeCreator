import pygame
import time

class KaraokeWordTiming:
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
            # rozbijamy linie na listy słów
            return [line.strip().split() for line in f if line.strip()]

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m:02d}:{s:05.2f}"

    def run(self):
        lyrics_lines = self.load_lyrics()
        timings = []  # lista: [(czas, słowo)]

        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("🎤 Timing – SPACE = następne słowo")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("arial", self.FONT_SIZE)

        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()

        start_time = time.time()
        current_line = 0
        current_word = 0
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

                    if event.key == pygame.K_SPACE:
                        now = time.time() - start_time
                        word = lyrics_lines[current_line][current_word]
                        timings.append((now, word))
                        current_word += 1
                        if current_word >= len(lyrics_lines[current_line]):
                            current_word = 0
                            current_line += 1
                            if current_line >= len(lyrics_lines):
                                running = False

            # ===== RYSOWANIE =====
            center_y = self.HEIGHT // 2
            start = max(0, current_line - self.LINES_BEFORE)
            end = min(len(lyrics_lines), current_line + self.LINES_AFTER + 1)
            y = center_y - (current_line - start) * self.LINE_SPACING

            for i in range(start, end):
                line_words = lyrics_lines[i]
                x = 50  # start X dla każdego wiersza

                for j, w in enumerate(line_words):
                    if i < current_line or (i == current_line and j < current_word):
                        color = self.PAST
                    elif i == current_line and j == current_word:
                        color = self.ACTIVE
                    else:
                        color = self.FUTURE

                    surf = font.render(w + " ", True, color)
                    screen.blit(surf, (x, y))
                    x += surf.get_width()
                y += self.LINE_SPACING

            pygame.display.flip()

        pygame.quit()

        # ===== ZAPIS LRC =====
        with open(self.output_lrc, "w", encoding="utf-8") as f:
            for t, word in timings:
                f.write(f"[{self.format_time(t)}]{word}\n")

        print("✅ Timing zapisany:", self.output_lrc)
