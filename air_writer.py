import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import math

# Initialize MediaPipe Hand Landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

# Project Settings (LinkedIn Style)
palette = [
    (0, 0, 1),       # Black
    (255, 0, 0),     # Blue
    (0, 255, 0),     # Green
    (0, 0, 255),     # Red
    (0, 255, 255),   # Yellow
    (255, 0, 255),   # Magenta
    (255, 128, 0),   # Orange
    (255, 255, 255)  # Eraser (White)
]
p_names = ["BLK", "BLU", "GRN", "RED", "YEL", "MAG", "ORN", "ERS"]
brush_sizes = [4, 10, 20, 40]
b_names = ["XS", "S", "M", "L"]

# Current State
draw_color = palette[0]
brush_thickness = brush_sizes[1]
is_whiteboard = True
canvas = None
prev_x, prev_y = 0, 0
smooth_factor = 5
points_history = []

def draw_skeleton(img, landmarks):
    connections = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (5,9), (9,10), (10,11), (11,12),
        (9,13), (13,14), (14,15), (15,16),
        (13,17), (17,18), (18,19), (19,20), (0,17)
    ]
    h, w, _ = img.shape
    for start, end in connections:
        p1 = (int(landmarks[start].x * w), int(landmarks[start].y * h))
        p2 = (int(landmarks[end].x * w), int(landmarks[end].y * h))
        cv2.line(img, p1, p2, (180, 180, 180), 1)
    for lm in landmarks:
        cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 3, (0, 255, 0), -1)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Starting LinkedIn-Style Virtual Board... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    if canvas is None: canvas = np.zeros((h, w, 3), np.uint8)

    display_img = np.ones((h, w, 3), np.uint8) * 255 if is_whiteboard else frame.copy()

    # Draw UI Header
    slots = len(palette) + 3
    sw = w // slots
    sh = 70
    for i, color in enumerate(palette):
        cv2.rectangle(display_img, (i * sw, 0), ((i + 1) * sw, sh), color, cv2.FILLED)
        cv2.rectangle(display_img, (i * sw, 0), ((i + 1) * sw, sh), (200, 200, 200), 1)
        tc = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
        cv2.putText(display_img, p_names[i], (i * sw + 5, sh - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, tc, 1)

    cv2.rectangle(display_img, (len(palette) * sw, 0), ((len(palette)+1) * sw, sh), (100, 100, 100), cv2.FILLED)
    cv2.putText(display_img, "CLR", (len(palette) * sw + 5, sh - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.rectangle(display_img, ((len(palette)+1) * sw, 0), ((len(palette)+2) * sw, sh), (50, 150, 50), cv2.FILLED)
    cv2.putText(display_img, "SAVE", ((len(palette)+1) * sw + 5, sh - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.rectangle(display_img, ((len(palette)+2) * sw, 0), (w, sh), (80, 80, 80), cv2.FILLED)
    cv2.putText(display_img, "MODE", ((len(palette)+2) * sw + 5, sh - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Brushes
    bh = 30
    bw = w // 10
    for i, size in enumerate(brush_sizes):
        c_bg = (200, 200, 200) if brush_thickness == size else (100, 100, 100)
        cv2.rectangle(display_img, (i * bw, sh), ((i + 1) * bw, sh + bh), c_bg, cv2.FILLED)
        cv2.rectangle(display_img, (i * bw, sh), ((i + 1) * bw, sh + bh), (0,0,0), 1)
        cv2.putText(display_img, f"SIZE {b_names[i]}", (i * bw + 5, sh + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,0), 1)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = detector.detect(mp_image)
    curr_gesture = "IDLE"

    if res.hand_landmarks:
        lms = res.hand_landmarks[0]
        draw_skeleton(display_img, lms)
        rx, ry = int(lms[8].x * w), int(lms[8].y * h)
        points_history.append((rx, ry))
        if len(points_history) > smooth_factor: points_history.pop(0)
        cx, cy = int(sum(p[0] for p in points_history)/len(points_history)), int(sum(p[1] for p in points_history)/len(points_history))

        idx_up = lms[8].y < lms[6].y
        mid_up = lms[12].y < lms[10].y
        
        if idx_up and mid_up:
            curr_gesture = "SELECTING"
            cv2.circle(display_img, (cx, cy), 15, (0, 255, 255), 2)
            prev_x, prev_y = 0, 0
            if cy < sh:
                idx = cx // sw
                if idx < len(palette): draw_color = palette[idx]
                elif idx == len(palette): canvas = np.zeros_like(frame)
                elif idx == len(palette) + 1:
                    cv2.imwrite(f"board_{time.strftime('%H%M%S')}.png", display_img); time.sleep(0.3)
                else: is_whiteboard = not is_whiteboard; time.sleep(0.3)
            elif cy < sh + bh:
                idx = cx // bw
                if idx < len(brush_sizes): brush_thickness = brush_sizes[idx]
        elif idx_up:
            curr_gesture = "DRAWING"
            cv2.circle(display_img, (cx, cy), brush_thickness//2, draw_color, cv2.FILLED)
            if prev_x != 0: cv2.line(canvas, (prev_x, prev_y), (cx, cy), draw_color, brush_thickness)
            prev_x, prev_y = cx, cy
        else: prev_x, prev_y = 0, 0

    cv2.putText(display_img, f"Gesture: {curr_gesture}", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    mask = cv2.threshold(cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY)[1]
    if is_whiteboard:
        display_img = cv2.add(cv2.bitwise_and(display_img, display_img, mask=cv2.bitwise_not(mask)), cv2.bitwise_and(canvas, canvas, mask=mask))
    else: display_img = cv2.addWeighted(display_img, 1, canvas, 1, 0)

    cv2.imshow("LinkedIn-Style Virtual Board", display_img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
detector.close()
