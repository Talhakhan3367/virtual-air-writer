# Virtual Air Writing Walkthrough

The Virtual Air Writing program allows you to draw in the air using your hand gestures captured by your laptop's camera.

## Features
- **Gestural Drawing**: Raise your index finger to start drawing on the screen.
- **Selection/Move Mode**: Raise both your index and middle fingers to move your "cursor" without drawing. This mode is also used to interact with the on-screen buttons.
- **On-Screen Buttons**:
    - **Blue, Green, Red, Yellow**: Change the ink color by hovering your fingers over these boxes at the top of the screen.
    - **Eraser**: Use the "Eraser" button to turn your finger into an eraser.
    - **CLEAR**: Hover over the grey "CLEAR" box to wipe the entire canvas.
- **Keyboard Shortcuts**:
    - Press `c` to clear the canvas.
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
