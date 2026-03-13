# Virtual Air Writing Walkthrough

The Virtual Air Writing program allows you to draw in the air using your hand gestures captured by your laptop's camera.

## Features
- **No-Touch Control**: Use hand motions only. No keyboard or mouse needed.
- **Pinch to Draw**: Bring your thumb and index finger together to start drawing.
- **Hover to Navigate**: Extend just your index finger to move the cursor without drawing.
- **Pinch to Click**: Hover over a button (Save, Clear, Colors) and pinch to activate it.
- **Palm Eraser**: Open your entire palm to use a large eraser.
- **Whiteboard Mode**: Start with a clean white board by default. Toggle back to the camera view using the "MODE" button.
- **On-Screen Buttons**:
    - **Black, Blue, Green, Red, Yellow**: Choose your ink color.
    - **CLEAR**: Wipe the entire canvas.
    - **SAVE**: Save your work as a `.png` image.
    - **MODE**: Switch between Whiteboard and Camera view.
- **Keyboard Shortcuts**:
    - Press `c` to clear the canvas.
    - Press `m` to toggle between Whiteboard and Camera mode.
    - Press `q` to quit the program.

## How to use
1. Run the program using the command: `python air_writer.py`.
2. Ensure you are in a well-lit area so the camera can clearly see your hand.
3. Position your hand so your fingers are visible to the camera.
4. **To Draw**: Keep your index finger up and middle finger down.
5. **To Select/Change Color**: Raise both index and middle fingers and move the cursor over the buttons at the top.

## Dependencies
- OpenCV (`cv2`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)

## Support Files
- **hand_landmarker.task**: This is the MediaPipe model file required for hand tracking. It must be in the same directory as `air_writer.py`.

## GitHub Integration
> [!NOTE]
> The program is ready to be pushed to GitHub. Please install `git` and let me know when you're ready to proceed with the repository initialization.
