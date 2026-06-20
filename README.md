Gesture-Controlled Puzzle Game
This project is an interactive puzzle game where the user manipulates on-screen shapes using hand gestures captured through a webcam. It leverages real-time computer vision to track hand movements and recognize a "pinch" gesture to grab and move objects.

The game is built with Python, using OpenCV for video processing and Google's MediaPipe for robust hand landmark detection.

![Placeholder for a GIF demo of the game in action. You can record your screen and add the GIF here.]

Features
Real-Time Gesture Control: Uses a standard webcam to track the user's hand and fingers in real-time.

Intuitive Pinch Gesture: Grab and drag objects by pinching your thumb, index, and middle fingers together.

Skeletal Tracking: Overlays the detected hand skeleton for clear visual feedback.

Smooth Cursor Movement: Implements an exponential moving average to filter out jitter and ensure smooth object dragging.

Dynamic & Randomized Puzzles: The starting positions of shapes and target placeholders are randomized on every replay for a new challenge each time.

Immersive UI: The entire game is rendered as an overlay on the live webcam feed.

Technologies Used
Python 3

OpenCV: For capturing and processing the webcam feed.

MediaPipe: For high-fidelity hand and finger tracking.

NumPy: For numerical operations and image manipulation.

Setup and Installation
Follow these steps to get the project running on your local machine.

1. Prerequisites

Make sure you have Python 3.7 or newer installed on your system.

2. Clone the Repository

git clone https://github.com/Raghavv7989/gesture-puzzle-game.git
cd gesture-puzzle-game

3. Install Dependencies

Install the required Python libraries using pip.

pip install opencv-python mediapipe numpy

How to Run
Execute the main script from your terminal:

python main.py

(Assuming you have named the script main.py)

A window will open, and the application will request access to your webcam.

How to Play
Move Your Hand: A skeletal structure and a cursor will follow your hand's movement.

Grab a Shape: Move the cursor over a shape and bring your thumb, index, and middle fingers together in a "pinch." The cursor will turn green, indicating you have grabbed the object.

Drag and Drop: Keep your fingers pinched to drag the shape to its matching placeholder on the right side of the screen.

Release: Open your fingers to release the shape. If it's close enough to the correct target, it will snap into place.

Win the Game: Place all shapes in their correct placeholders to win.

Controls:

Press 'q' to quit the game at any time.

After winning, press 'r' to restart and play a new randomized puzzle.
