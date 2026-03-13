import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

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

# Canvas for drawing
canvas = None
prev_x, prev_y = 0, 0
draw_color = (0, 0, 0) # Black (Initial for whiteboard)
brush_thickness = 10
eraser_thickness = 50

# Mode Settings
is_whiteboard = True

# UI Settings
colors = [
    (0, 0, 0),     # Black
    (255, 0, 0),   # Blue
    (0, 255, 0),   # Green
    (0, 0, 255),   # Red
    (0, 255, 255), # Yellow
    (255, 255, 255)# Eraser (White on canvas in whiteboard mode)
]
color_names = ["Black", "Blue", "Green", "Red", "Yellow", "Eraser"]

# Camera Capture
cap = cv2.VideoCapture(0)

print("Starting Virtual Air Writer (Whiteboard Mode)... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Flip the image horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)

    # Determine Background
    if is_whiteboard:
        display_img = np.ones((h, w, 3), np.uint8) * 255
    else:
        display_img = frame.copy()

    # Draw UI Header Buttons
    # Adding one more button for the mode toggle
    total_buttons = len(colors) + 2 # Colors + Clear + Toggle
    button_w = w // total_buttons
    
    for i, color in enumerate(colors):
        # Draw color buttons
        cv2.rectangle(display_img, (i * button_w, 0), ((i + 1) * button_w, 100), color, cv2.FILLED)
        # Border
        cv2.rectangle(display_img, (i * button_w, 0), ((i + 1) * button_w, 100), (200, 200, 200), 2)
        
        text = color_names[i]
        font_scale = 0.5
        text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = i * button_w + (button_w - text_size[0]) // 2
        cv2.putText(display_img, text, (text_x, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    # Clear Button
    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (128, 128, 128), cv2.FILLED)
    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (200, 200, 200), 2)
    cv2.putText(display_img, "CLEAR", (len(colors) * button_w + 10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Mode Toggle Button
    toggle_text = "MODE: BOARD" if is_whiteboard else "MODE: CAM"
    cv2.rectangle(display_img, ((len(colors)+1) * button_w, 0), (w, 100), (80, 80, 80), cv2.FILLED)
    cv2.rectangle(display_img, ((len(colors)+1) * button_w, 0), (w, 100), (200, 200, 200), 2)
    cv2.putText(display_img, toggle_text, ((len(colors)+1) * button_w + 10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Convert to MediaPipe Image (Always use the actual frame for detection)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    # Detect hand landmarks
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        hand_lms = detection_result.hand_landmarks[0]
        
        index_tip = hand_lms[8]
        index_mcp = hand_lms[5]
        middle_tip = hand_lms[12]
        middle_mcp = hand_lms[9]
        
        ix, iy = int(index_tip.x * w), int(index_tip.y * h)
        
        index_up = index_tip.y < index_mcp.y
        middle_up = middle_tip.y < middle_mcp.y

        if index_up and middle_up:
            # SELECTION MODE
            prev_x, prev_y = 0, 0
            cv2.circle(display_img, (ix, iy), 15, draw_color, cv2.FILLED)
            cv2.circle(display_img, (ix, iy), 17, (255, 255, 255), 2)
            
            # Button collisions
            if iy < 100:
                if ix < len(colors) * button_w:
                    selected_idx = ix // button_w
                    draw_color = colors[selected_idx]
                    if color_names[selected_idx] == "Eraser":
                        brush_thickness = eraser_thickness
                    else:
                        brush_thickness = 10
                elif ix < (len(colors)+1) * button_w:
                    # Clear Canvas
                    canvas = np.zeros_like(frame)
                    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (0, 255, 0), cv2.FILLED)
                else:
                    # Toggle Mode (Add delay to avoid flickering)
                    is_whiteboard = not is_whiteboard
                    time.sleep(0.3) 

        elif index_up and not middle_up:
            # DRAWING MODE
            cv2.circle(display_img, (ix, iy), brush_thickness, draw_color, cv2.FILLED)
            
            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = ix, iy
            
            # Draw on canvas
            cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, brush_thickness)
            prev_x, prev_y = ix, iy
        else:
            prev_x, prev_y = 0, 0

    # Combine Canvas with Background
    if is_whiteboard:
        # For whiteboard, we want the canvas strokes to overwrite the white background
        # Since canvas is black (0,0,0) by default, we need to handle the transparency
        canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(canvas_gray, 10, 255, cv2.THRESH_BINARY)
        inv_mask = cv2.bitwise_not(mask)
        
        # Area where strokes are: just use the canvas
        # Area where strokes are NOT: use the display_img (white background)
        bg_part = cv2.bitwise_and(display_img, display_img, mask=inv_mask)
        canvas_part = cv2.bitwise_and(canvas, canvas, mask=mask)
        display_img = cv2.add(bg_part, canvas_part)
    else:
        # For camera mode, use the previous logic
        display_img = cv2.addWeighted(display_img, 1, canvas, 1, 0)

    cv2.imshow("Virtual Air Writer", display_img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros_like(frame)
    elif key == ord('m'):
        is_whiteboard = not is_whiteboard

cap.release()
cv2.destroyAllWindows()
detector.close()

cap.release()
cv2.destroyAllWindows()
detector.close()
