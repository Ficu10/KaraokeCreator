import cv2
import json
import numpy as np
import imageio.v2 as imageio
import os

# --- KONFIG ---
IMAGE_DIR = "images_cropped"
POINTS_FILE = "points.json"
OUTPUT = "output2.mp4"

FPS = 30
HOLD_SECONDS = 5
TRANSITION_SECONDS = 3.0

FADE_DELAY = 0.5          # opóźnienie zanikania tła
FACE_MORPH_DELAY = 0.5   # kiedy zaczyna się zmiana wyglądu twarzy
BLUR_MAX = 25

HOLD_FRAMES = int(HOLD_SECONDS * FPS)
TRANSITION_FRAMES = int(TRANSITION_SECONDS * FPS)
fade_offset = int(FADE_DELAY * FPS)
face_offset = int(FACE_MORPH_DELAY * FPS)

# --- DANE ---
with open(POINTS_FILE) as f:
    points = json.load(f)

images = sorted(os.listdir(IMAGE_DIR))
imgs = []

for f in images:
    img = cv2.imread(os.path.join(IMAGE_DIR, f))
    h, w = img.shape[:2]
    w += w % 2
    h += h % 2
    img = cv2.resize(img, (w, h))
    imgs.append(img.astype(np.float32))

h, w = imgs[0].shape[:2]

# --- FUNKCJE ---
def ease(t):
    return t * t * (3 - 2 * t)

def estimate_affine(p1, p2):
    M, _ = cv2.estimateAffinePartial2D(
        np.array(p1[:3], np.float32),
        np.array(p2[:3], np.float32)
    )
    return M

def face_mask(pts, shape):
    mask = np.zeros(shape[:2], dtype=np.uint8)
    hull = cv2.convexHull(pts.astype(np.int32))
    cv2.fillConvexPoly(mask, hull, 255)
    mask = cv2.GaussianBlur(mask, (51, 51), 0)
    return (mask / 255.0).astype(np.float32)

# --- WIDEO ---
writer = imageio.get_writer(
    OUTPUT, fps=FPS, codec="libx264", macro_block_size=1
)

for i in range(len(imgs) - 1):
    img1 = imgs[i]
    img2 = imgs[i + 1]

    pts1 = np.array(points[images[i]], np.float32)
    pts2 = np.array(points[images[i + 1]], np.float32)

    M_target = estimate_affine(pts1, pts2)
    I = np.array([[1, 0, 0], [0, 1, 0]], np.float32)

    mask = face_mask(pts2, img2.shape)

    # pauza
    for _ in range(HOLD_FRAMES):
        writer.append_data(cv2.cvtColor(img1.astype(np.uint8), cv2.COLOR_BGR2RGB))

    # TRANSITION
    for f in range(TRANSITION_FRAMES):
        t = f / TRANSITION_FRAMES
        t_e = ease(t)

        # 🔹 ruch twarzy
        M = I * (1 - t_e) + M_target * t_e
        aligned1 = cv2.warpAffine(img1, M, (w, h), borderMode=cv2.BORDER_REFLECT)

        # 🔹 morph wyglądu twarzy
        if f < face_offset:
            face_t = 0.0
        else:
            face_t = ease((f - face_offset) / (TRANSITION_FRAMES - face_offset))

        face_mix = aligned1 * (1 - face_t) + img2 * face_t

        # 🔹 tło rozmywane
        blur_k = int(1 + BLUR_MAX * t_e)
        blur_k += blur_k % 2 == 0
        blurred = cv2.GaussianBlur(aligned1, (blur_k, blur_k), 0)

        composed = (
            face_mix * mask[..., None] +
            blurred * (1 - mask[..., None])
        )

        # 🔹 fade tła
        if f < fade_offset:
            fade_t = 0.0
        else:
            fade_t = ease((f - fade_offset) / (TRANSITION_FRAMES - fade_offset))

        frame = composed * (1 - fade_t) + img2 * fade_t
        frame = np.clip(frame, 0, 255).astype(np.uint8)

        writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# ostatnie zdjęcie
for _ in range(HOLD_FRAMES):
    writer.append_data(cv2.cvtColor(imgs[-1].astype(np.uint8), cv2.COLOR_BGR2RGB))

writer.close()
print("✅ Gotowe: output.mp4")
