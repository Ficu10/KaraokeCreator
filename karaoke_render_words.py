import pygame
import numpy as np
import moviepy.editor as mp
import re
import math

WIDTH, HEIGHT = 1280, 720
FPS = 30
FONT_SIZE = 50
LINE_SPACING = 55
CENTER_Y = HEIGHT // 2

WHITE = (230, 230, 230)
RED = (255, 80, 80)
BG = (0, 0, 0)

# ===== Funkcja wczytująca LRC słów =====
def load_lrc_words(path):
    pattern = re.compile(r"\[(\d+):(\d+\.\d+)-(\d+):(\d+\.\d+)\](.*)")
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                start = int(m.group(1))*60 + float(m.group(2))
                end = int(m.group(3))*60 + float(m.group(4))
                word = m.group(5).strip()
                out.append((start, end, word))
    return out

# ===== Render słów =====
def render_karaoke_words(instrumental, lrc_file, output_mp4):
    words = load_lrc_words(lrc_file)
    if not words:
        raise RuntimeError("❌ LRC jest pusty")

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("arial", FONT_SIZE)

    audio = mp.AudioFileClip(instrumental)
    duration = audio.duration
    total_frames = int(math.ceil(duration * FPS))
    frames = []

    print("🎬 Render klatek:", total_frames)

    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        screen = pygame.Surface((WIDTH, HEIGHT))
        screen.fill(BG)

        # ===== RYSOWANIE SŁÓW =====
        y = CENTER_Y
        for start, end, word in words:
            if start <= t <= end:
                color = RED
            elif t > end:
                color = (180,180,180)
            else:
                color = WHITE

            surf = font.render(word, True, color)
            rect = surf.get_rect(center=(WIDTH//2, y))
            screen.blit(surf, rect)
            y += LINE_SPACING

        # ===== FRAME =====
        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1,0,2))  # (H,W,RGB)
        frames.append(frame)

    pygame.quit()

    print("🎞 Składanie wideo...")
    clip = mp.ImageSequenceClip(frames, fps=FPS)
    clip = clip.set_audio(audio)
    clip.write_videofile(
        output_mp4,
        codec="libx264",
        audio_codec="aac",
        fps=FPS
    )

    print("✅ Karaoke słów zapisane:", output_mp4)
