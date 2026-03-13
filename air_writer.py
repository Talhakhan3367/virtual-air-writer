import cv2
import numpy as np
import mediapipe as mp
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Canvas for drawing
canvas = None
prev_x, prev_y = 0, 0
draw_color = (0, 255, 0) # Green (Initial)
brush_thickness = 5
eraser_thickness = 50

# UI Settings
colors = [
    (255, 0, 0),   # Blue
    (0, 255, 0),   # Green
    (0, 0, 255),   # Red
    (0, 255, 255), # Yellow
    (0, 0, 0)      # Eraser (Black on canvas)
]
color_names = ["Blue", "Green", "Red", "Yellow", "Eraser"]

# Camera Capture
cap = cv2.VideoCapture(0)

print("Starting Air Writer... Press 'q' to quit.")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Flip the image horizontally for a mirror effect
    img = cv2.flip(img, 1)
    h, w, c = img.shape
    
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)

    # Draw UI Header Buttons
    # Each button will be roughly 120 pixels wide
    button_w = w // (len(colors) + 1)
    for i, color in enumerate(colors):
        cv2.rectangle(img, (i * button_w, 0), ((i + 1) * button_w, 100), color, cv2.FILLED)
        text = color_names[i]
        font_scale = 0.6
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = i * button_w + (button_w - text_size[0]) // 2
        cv2.putText(img, text, (text_x, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    # Clear Button
    cv2.rectangle(img, (len(colors) * button_w, 0), (w, 100), (128, 128, 128), cv2.FILLED)
    cv2.putText(img, "CLEAR", (len(colors) * button_w + 20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Convert to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Get coordinates for Index Finger Tip (8) and Middle Finger Tip (12)
            index_tip = hand_lms.landmark[8]
            middle_tip = hand_lms.landmark[12]
            
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            mx, my = int(middle_tip.x * w), int(middle_tip.y * h)

            # Finger status
            index_up = index_tip.y < hand_lms.landmark[6].y
            middle_up = middle_tip.y < hand_lms.landmark[10].y

            if index_up and middle_up:
                # SELECTION MODE (Moving without drawing)
                prev_x, prev_y = 0, 0
                cv2.circle(img, (ix, iy), 15, draw_color, cv2.FILLED)
                
                # Check for button collisions
                if iy < 100:
                    if ix < len(colors) * button_w:
                        # Change color
                        selected_idx = ix // button_w
                        draw_color = colors[selected_idx]
                        if color_names[selected_idx] == "Eraser":
                            brush_thickness = eraser_thickness
                        else:
                            brush_thickness = 10
                    else:
                        # Clear Canvas
                        canvas = np.zeros_like(img)
                        cv2.rectangle(img, (len(colors) * button_w, 0), (w, 100), (0, 255, 0), cv2.FILLED)

            elif index_up and not middle_up:
                # DRAWING MODE
                cv2.circle(img, (ix, iy), brush_thickness, draw_color, cv2.FILLED)
                
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = ix, iy
                
                # Draw on canvas
                # Note: Eraser is just drawing black on the canvas
                cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, brush_thickness)
                prev_x, prev_y = ix, iy
            else:
                prev_x, prev_y = 0, 0

    # Overlay Canvas on Camera Feed
    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_BGR2RGB) # Ensure correct conversion
    
    # Simple addition/masking for overlay
    img = cv2.addWeighted(img, 1, canvas, 1, 0)

    cv2.imshow("Virtual Air Writer", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros_like(img)

cap.release()
cv2.destroyAllWindows()
