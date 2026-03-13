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
draw_color = (0, 255, 0) # Green (Initial)
brush_thickness = 10
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

print("Starting Virtual Air Writer (Tasks API)... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Flip the image horizontally for a mirror effect
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)

    # Draw UI Header Buttons
    button_w = w // (len(colors) + 1)
    for i, color in enumerate(colors):
        cv2.rectangle(frame, (i * button_w, 0), ((i + 1) * button_w, 100), color, cv2.FILLED)
        text = color_names[i]
        font_scale = 0.6
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = i * button_w + (button_w - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    # Clear Button
    cv2.rectangle(frame, (len(colors) * button_w, 0), (w, 100), (128, 128, 128), cv2.FILLED)
    cv2.putText(frame, "CLEAR", (len(colors) * button_w + 20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    # Detect hand landmarks
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        # Get the first hand
        hand_lms = detection_result.hand_landmarks[0]
        
        # Landmark indices: 
        # Index Tip: 8
        # Index MCP: 5
        # Middle Tip: 12
        # Middle MCP: 9
        
        index_tip = hand_lms[8]
        index_mcp = hand_lms[5]
        middle_tip = hand_lms[12]
        middle_mcp = hand_lms[9]
        
        ix, iy = int(index_tip.x * w), int(index_tip.y * h)
        mx, my = int(middle_tip.x * w), int(middle_tip.y * h)

        # Simplified gesture detection (finger up if tip is above MCP)
        index_up = index_tip.y < index_mcp.y
        middle_up = middle_tip.y < middle_mcp.y

        if index_up and middle_up:
            # SELECTION MODE
            prev_x, prev_y = 0, 0
            cv2.circle(frame, (ix, iy), 15, draw_color, cv2.FILLED)
            
            # Button collisions
            if iy < 100:
                if ix < len(colors) * button_w:
                    selected_idx = ix // button_w
                    draw_color = colors[selected_idx]
                    if color_names[selected_idx] == "Eraser":
                        brush_thickness = eraser_thickness
                    else:
                        brush_thickness = 10
                else:
                    canvas = np.zeros_like(frame)
                    cv2.rectangle(frame, (len(colors) * button_w, 0), (w, 100), (0, 255, 0), cv2.FILLED)

        elif index_up and not middle_up:
            # DRAWING MODE
            cv2.circle(frame, (ix, iy), brush_thickness, draw_color, cv2.FILLED)
            
            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = ix, iy
            
            cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, brush_thickness)
            prev_x, prev_y = ix, iy
        else:
            prev_x, prev_y = 0, 0

    # Overlay Canvas on Camera Feed
    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY_INV)
    
    # Combine
    frame = cv2.addWeighted(frame, 1, canvas, 1, 0)

    cv2.imshow("Virtual Air Writer", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros_like(frame)

cap.release()
cv2.destroyAllWindows()
detector.close()
