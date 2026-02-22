import pygame
import numpy as np
import moviepy.editor as mp
import re
import math

WIDTH, HEIGHT = 1280, 720
FPS = 24  # Zmieniono z 30 -> 24 FPS (20% szybciej, imperceptible dla odbiorcy)
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
def render_karaoke_words(instrumental, lrc_file, output_mp4, progress_callback=None):
    """
    Renderuje video karaoke ze słowami.
    
    Args:
        instrumental: ścieżka do instrumentu WAV
        lrc_file: ścieżka do pliku LRC
        output_mp4: ścieżka do zapisu MP4
        progress_callback: funkcja callback(current, max, text) do aktualizacji progressbaru
    """
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

    print(f"🎬 Render klatek: {total_frames} (czas: {duration:.1f}s, FPS: {FPS})")

    for frame_idx in range(total_frames):
        # Progressbar co 30 ramek
        if frame_idx % 30 == 0:
            progress_pct = (frame_idx / total_frames) * 100
            status = f"Ramki: {frame_idx}/{total_frames}"
            print(f"   ⏳ {status} ({progress_pct:.1f}%)")
            if progress_callback:
                progress_callback(frame_idx, total_frames, status)

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

    print("🎞 Składanie wideo (kodowanie optimized)...")
    if progress_callback:
        progress_callback(total_frames * 0.7, total_frames * 1.5, "Kodowanie MP4")
    
    clip = mp.ImageSequenceClip(frames, fps=FPS)
    clip = clip.set_audio(audio)
    
    # Optymalizacje dla szybszego kodowania:
    # - preset='ultrafast': szybkie kodowanie bez dużej straty jakości
    # - verbose=False: wyłacza verbose output MoviePy
    clip.write_videofile(
        output_mp4,
        codec="libx264",
        preset="ultrafast",  # 🚀 Szybciej
        audio_codec="aac",
        fps=FPS,
        verbose=False,
        logger=None
    )

    print("✅ Karaoke słów zapisane:", output_mp4)
