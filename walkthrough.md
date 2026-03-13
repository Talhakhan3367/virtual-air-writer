# Virtual Air Writing Walkthrough

The Virtual Air Writing program allows you to draw in the air using your hand gestures captured by your laptop's camera.

## Features
- **Professional Interface**: 8 Colors and 4 Brush Sizes selectable from the top menu.
- **Drawing Mode (Index Finger Only)**: Raise just your index finger to write on the board. UI interaction is locked during this mode for safety.
- **Selection Mode (Index + Middle Fingers)**: Raise both fingers to use your index finger as a pointer. Hover over menu items to change colors, sizes, or save your work.
- **Visual Skeleton**: A real-time hand skeleton overlay shows you exactly how the AI is tracking your hand.
- **On-Screen Menu**:
    - **8 Palette Colors**: Black, Blue, Green, Red, Yellow, Magenta, Orange, Eraser.
    - **4 Brush Sizes**: Select XS, S, M, or L for precision or bold strokes.
    - **CLR**: Instantly wipe the entire board.
    - **SAVE**: Export your board as a high-quality `.png` image.
    - **MODE**: Toggle between solid Whiteboard and live Camera views.
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
