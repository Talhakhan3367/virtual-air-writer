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
    (0, 0, 1),     # Black (using 1 instead of 0 for mask detection)
    (255, 0, 0),   # Blue
    (0, 255, 0),   # Green
    (0, 0, 255),   # Red
    (0, 255, 255), # Yellow
    (255, 255, 255)# Eraser
]
color_names = ["Black", "Blue", "Green", "Red", "Yellow", "Eraser"]

# Camera Capture
cap = cv2.VideoCapture(0)

# Set common resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Starting Virtual Air Writer... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Camera access failed. Ensure no other app is using the camera.")
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
    # Adding buttons for Save and Undo as well
    # Colors + Clear + Mode + Save
    total_buttons = len(colors) + 3 
    button_w = w // total_buttons
    
    for i, color in enumerate(colors):
        # Draw color buttons
        cv2.rectangle(display_img, (i * button_w, 0), ((i + 1) * button_w, 100), color, cv2.FILLED)
        cv2.rectangle(display_img, (i * button_w, 0), ((i + 1) * button_w, 100), (200, 200, 200), 1)
        
        text = color_names[i]
        font_scale = 0.5
        text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = i * button_w + (button_w - text_size[0]) // 2
        cv2.putText(display_img, text, (text_x, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    # Clear Button
    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (128, 128, 128), cv2.FILLED)
    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (200, 200, 200), 1)
    cv2.putText(display_img, "CLEAR", (len(colors) * button_w + 5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Save Button
    cv2.rectangle(display_img, ((len(colors)+1) * button_w, 0), ((len(colors)+2) * button_w, 100), (50, 150, 50), cv2.FILLED)
    cv2.rectangle(display_img, ((len(colors)+1) * button_w, 0), ((len(colors)+2) * button_w, 100), (200, 200, 200), 1)
    cv2.putText(display_img, "SAVE", ((len(colors)+1) * button_w + 10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Mode Toggle Button
    mode_bg = (80, 80, 80) if is_whiteboard else (150, 50, 50)
    cv2.rectangle(display_img, ((len(colors)+2) * button_w, 0), (w, 100), mode_bg, cv2.FILLED)
    cv2.rectangle(display_img, ((len(colors)+2) * button_w, 0), (w, 100), (200, 200, 200), 1)
    toggle_text = "BOARD" if is_whiteboard else "CAM"
    cv2.putText(display_img, toggle_text, ((len(colors)+2) * button_w + 5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    # Detect
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        hand_lms = detection_result.hand_landmarks[0]
        index_tip = hand_lms[8]
        index_mcp = hand_lms[5]
        middle_tip = hand_lms[12]
        middle_mcp = hand_lms[9]
        
        ix, iy = int(index_tip.x * w), int(index_tip.y * h)
        
        # Skeleton ghost (optional feedback)
        for lm in hand_lms:
            cv2.circle(display_img, (int(lm.x * w), int(lm.y * h)), 3, (150, 150, 150), -1)

        index_up = index_tip.y < index_mcp.y
        middle_up = middle_tip.y < middle_mcp.y

        if index_up and middle_up:
            # SELECTION MODE
            prev_x, prev_y = 0, 0
            cv2.circle(display_img, (ix, iy), 15, draw_color, cv2.FILLED)
            cv2.circle(display_img, (ix, iy), 18, (100, 100, 100), 2)
            
            # Button collisions
            if iy < 100:
                if ix < len(colors) * button_w:
                    selected_idx = ix // button_w
                    draw_color = colors[selected_idx]
                    brush_thickness = eraser_thickness if color_names[selected_idx] == "Eraser" else 10
                elif ix < (len(colors)+1) * button_w:
                    canvas = np.zeros_like(frame)
                    cv2.rectangle(display_img, (len(colors) * button_w, 0), ((len(colors)+1) * button_w, 100), (0, 255, 0), cv2.FILLED)
                elif ix < (len(colors)+2) * button_w:
                    # Save
                    filename = f"whiteboard_{time.strftime('%H%M%S')}.png"
                    cv2.imwrite(filename, display_img)
                    cv2.putText(display_img, "SAVED", (w//2-50, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    time.sleep(0.3)
                else:
                    # Toggle Mode
                    is_whiteboard = not is_whiteboard
                    time.sleep(0.3) 

        elif index_up and not middle_up:
            # DRAWING MODE
            cv2.circle(display_img, (ix, iy), brush_thickness, draw_color, cv2.FILLED)
            
            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = ix, iy
            
            cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, brush_thickness)
            prev_x, prev_y = ix, iy
        else:
            prev_x, prev_y = 0, 0

    # Combine Canvas with Background
    # Using a more robust masking technique
    canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(canvas_gray, 0, 255, cv2.THRESH_BINARY) # Changed threshold to 0
    inv_mask = cv2.bitwise_not(mask)
    
    if is_whiteboard:
        bg_part = cv2.bitwise_and(display_img, display_img, mask=inv_mask)
        # Note: Canvas background is naturally black, so we just add it
        canvas_part = cv2.bitwise_and(canvas, canvas, mask=mask)
        display_img = cv2.add(bg_part, canvas_part)
        
        # Add a mini camera preview so the user knows where they are
        mini_preview = cv2.resize(frame, (160, 90))
        display_img[h-100:h-10, 10:170] = mini_preview
        cv2.rectangle(display_img, (10, h-100), (170, h-10), (0, 255, 0), 2)
    else:
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
