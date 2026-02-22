import pygame
import re
import numpy as np
import moviepy.editor as mp
import bisect
import math

# ================= USTAWIENIA =================
WIDTH, HEIGHT = 1280, 720
FPS = 30
FONT_SIZE = 42
COUNTDOWN_FONT_SIZE = 120
LINE_SPACING = 55
CENTER_Y = HEIGHT // 2
LINES_ON_SCREEN = 17
COUNTDOWN_SECONDS = 3

WHITE = (230, 230, 230)
RED = (255, 80, 80)
BG = (0, 0, 0)
# =============================================


def load_lrc(path):
    pattern = re.compile(r"\[(\d+):(\d+\.\d+)\](.*)")
    out = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                t = int(m.group(1)) * 60 + float(m.group(2))
                text = m.group(3).strip()
                if text:
                    out.append((t, text))
    return out


def render_karaoke(instrumental, lrc_file, output_mp4):
    lyrics = load_lrc(lrc_file)
    if not lyrics:
        raise RuntimeError("❌ Plik LRC jest pusty")

    times = [t for t, _ in lyrics]
    first_time = times[0]

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("arial", FONT_SIZE)
    countdown_font = pygame.font.SysFont("arial", COUNTDOWN_FONT_SIZE, bold=True)

    audio = mp.AudioFileClip(instrumental)
    duration = audio.duration

    total_frames = int(math.ceil(duration * FPS))
    frames = []

    print("🎬 Render klatek:", total_frames)

    for frame_idx in range(total_frames):
        t = frame_idx / FPS

        screen = pygame.Surface((WIDTH, HEIGHT))
        screen.fill(BG)

        # ===== WYBÓR AKTYWNEJ LINII =====
        if t < first_time:
            active = 0
            progress = 0.0
        else:
            active = bisect.bisect_right(times, t) - 1
            active = max(0, min(active, len(lyrics) - 1))

            if active < len(times) - 1:
                t1 = times[active]
                t2 = times[active + 1]
                span = max(0.05, t2 - t1)
                progress = max(0.0, min(1.0, (t - t1) / span))
            else:
                progress = 0.0

        offset = progress * LINE_SPACING

        # ===== RYSUJ TEKST =====
        start = max(0, active - LINES_ON_SCREEN // 2)
        end = min(len(lyrics), start + LINES_ON_SCREEN)

        for i in range(start, end):
            is_active = (i == active and t >= first_time)
            color = RED if is_active else WHITE

            surf = font.render(lyrics[i][1], True, color)
            x = (WIDTH - surf.get_width()) // 2
            y = CENTER_Y + (i - active) * LINE_SPACING - offset
            screen.blit(surf, (x, y))

        # ===== COUNTDOWN NAD TEKSTEM =====
        if first_time - COUNTDOWN_SECONDS <= t < first_time:
            remaining = int(math.ceil(first_time - t))
            remaining = max(1, min(remaining, COUNTDOWN_SECONDS))

            cd_surf = countdown_font.render(str(remaining), True, RED)
            cd_rect = cd_surf.get_rect(
                center=(WIDTH // 2, CENTER_Y - LINE_SPACING * 2)
            )
            screen.blit(cd_surf, cd_rect)

        # ===== FRAME =====
        frame = pygame.surfarray.array3d(screen)
        frame = np.transpose(frame, (1, 0, 2))  # (H,W,RGB)
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

    print("✅ Karaoke zapisane:", output_mp4)
