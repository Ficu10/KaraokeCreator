import cv2
import json
import os

IMAGE_DIR = "images_cropped"
POINTS_FILE = "points.json"

POINT_NAMES = ["left_eye", "right_eye", "nose", "mouth"]

points_data = {}
current_points = []
scale = 1.0
img_orig = None
img_display = None

def fit_to_screen(img, max_w=1400, max_h=800):
    h, w = img.shape[:2]
    s = min(max_w / w, max_h / h, 1.0)
    return cv2.resize(img, (int(w * s), int(h * s))), s

def click(event, x, y, flags, param):
    global current_points
    if event == cv2.EVENT_LBUTTONDOWN:
        ox = int(x / scale)
        oy = int(y / scale)
        current_points.append((ox, oy))
        print(f"{POINT_NAMES[len(current_points)-1]}: {ox}, {oy}")

def mark_image(path):
    global current_points, scale, img_orig, img_display
    current_points = []

    img_orig = cv2.imread(path)
    img_display, scale = fit_to_screen(img_orig)

    cv2.namedWindow("Zaznacz punkty", cv2.WINDOW_NORMAL)
    cv2.imshow("Zaznacz punkty", img_display)
    cv2.setMouseCallback("Zaznacz punkty", click)

    print("\nKliknij kolejno:")
    for p in POINT_NAMES:
        print(" -", p)

    while True:
        display = img_display.copy()
        for x, y in current_points:
            dx = int(x * scale)
            dy = int(y * scale)
            cv2.circle(display, (dx, dy), 6, (0, 255, 0), -1)

        cv2.imshow("Zaznacz punkty", display)

        if len(current_points) == len(POINT_NAMES):
            break

        if cv2.waitKey(1) == 27:
            exit()

    cv2.destroyAllWindows()
    return current_points

images = sorted(os.listdir(IMAGE_DIR))

for img_name in images:
    path = os.path.join(IMAGE_DIR, img_name)
    print(f"\n➡️ {img_name}")
    pts = mark_image(path)
    points_data[img_name] = pts

with open(POINTS_FILE, "w") as f:
    json.dump(points_data, f, indent=2)

print("\n✅ Zapisano points.json")
