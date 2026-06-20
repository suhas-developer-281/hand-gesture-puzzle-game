import cv2
import mediapipe as mp
import numpy as np
import math
import random

# --- Setup ---

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# --- MODIFIED: Removed 'enable_segmentation' to fix compatibility error ---
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
    static_image_mode=False
)

# Initialize Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open webcam.")
    exit()

# Set webcam resolution
cap.set(3, 1280)
cap.set(4, 720)

# --- Game Configuration ---

# Canvas dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Shape properties
SHAPE_SIZE = 60
SNAP_DISTANCE = 45 # Slightly increased snap distance for easier placement
PINCH_THRESHOLD = 0.08 # Fine-tuned threshold for better pinch detection

# Smoothing factor for the cursor
SMOOTHING_FACTOR = 0.85

# Colors (B, G, R)
COLORS = {
    'red': (44, 44, 239),
    'blue': (246, 130, 59),
    'green': (94, 197, 34),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'yellow_cursor': (0, 255, 255),
    'green_cursor': (0, 255, 0),
    'mask_color': (200, 170, 0) # A light blue for the hand mask
}

# Shape definitions
SHAPE_DEFS = [
    {'type': 'square', 'color': 'red'},
    {'type': 'circle', 'color': 'blue'},
    {'type': 'triangle', 'color': 'green'}
]

# Game state variables
shapes = []
placeholders = []
held_shape = None
pinch_state = {'is_pinching': False, 'pos': (0, 0)}
game_won = False
smooth_cursor_pos = (0, 0)

# --- Helper Functions ---

def draw_shape(image, shape_info, is_placeholder=False):
    """Draws a single shape on the image."""
    color = COLORS[shape_info['color']]
    center_x, center_y = int(shape_info['x']), int(shape_info['y'])

    if is_placeholder:
        thickness = 3
        if shape_info['type'] == 'square':
            cv2.rectangle(image, (center_x - SHAPE_SIZE // 2, center_y - SHAPE_SIZE // 2),
                          (center_x + SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2), color, thickness)
        elif shape_info['type'] == 'circle':
            cv2.circle(image, (center_x, center_y), SHAPE_SIZE // 2, color, thickness)
        elif shape_info['type'] == 'triangle':
            points = np.array([
                (center_x, center_y - SHAPE_SIZE // 2),
                (center_x + SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2),
                (center_x - SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2)
            ], np.int32)
            cv2.polylines(image, [points], isClosed=True, color=color, thickness=thickness)
    else:
        if shape_info['type'] == 'square':
            cv2.rectangle(image, (center_x - SHAPE_SIZE // 2, center_y - SHAPE_SIZE // 2),
                          (center_x + SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2), color, -1)
        elif shape_info['type'] == 'circle':
            cv2.circle(image, (center_x, center_y), SHAPE_SIZE // 2, color, -1)
        elif shape_info['type'] == 'triangle':
            points = np.array([
                (center_x, center_y - SHAPE_SIZE // 2),
                (center_x + SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2),
                (center_x - SHAPE_SIZE // 2, center_y + SHAPE_SIZE // 2)
            ], np.int32)
            cv2.fillPoly(image, [points], color)

def initialize_game():
    """Sets up or resets the game state with randomized positions."""
    global shapes, placeholders, held_shape, game_won, smooth_cursor_pos
    shapes = []
    placeholders = []
    held_shape = None
    game_won = False
    smooth_cursor_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    num_items = len(SHAPE_DEFS)
    shape_indices = list(range(num_items))
    placeholder_indices = list(range(num_items))
    random.shuffle(shape_indices)
    random.shuffle(placeholder_indices)

    for i in range(num_items):
        s_def = SHAPE_DEFS[i]
        p_idx = placeholder_indices[i]
        placeholders.append({
            'type': s_def['type'], 'color': s_def['color'],
            'x': SCREEN_WIDTH - SHAPE_SIZE * 1.5,
            'y': SHAPE_SIZE * 1.5 + (SHAPE_SIZE * 2.5) * p_idx
        })

    for i in range(num_items):
        s_def = SHAPE_DEFS[i]
        s_idx = shape_indices[i]
        shapes.append({
            'type': s_def['type'], 'color': s_def['color'],
            'x': SHAPE_SIZE * 1.5,
            'y': SHAPE_SIZE * 1.5 + (SHAPE_SIZE * 2.5) * s_idx,
            'is_snapped': False,
            'target_placeholder': next(p for p in placeholders if p['type'] == s_def['type'])
        })

# --- Main Game Loop ---

initialize_game()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    raw_cursor_pos = smooth_cursor_pos
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Draw the hand skeleton
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

        # --- MODIFIED: Removed hand mask drawing logic ---

        # --- Gameplay logic continues below ---
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

        dist_thumb_index = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
        dist_thumb_middle = math.hypot(thumb_tip.x - middle_tip.x, thumb_tip.y - middle_tip.y)
        avg_dist = (dist_thumb_index + dist_thumb_middle) / 2

        raw_cursor_x = int(((thumb_tip.x + index_tip.x) / 2) * SCREEN_WIDTH)
        raw_cursor_y = int(((thumb_tip.y + index_tip.y) / 2) * SCREEN_HEIGHT)
        raw_cursor_pos = (raw_cursor_x, raw_cursor_y)
        
        is_pinching_now = avg_dist < PINCH_THRESHOLD
        
        if is_pinching_now and not pinch_state['is_pinching']:
            pinch_state['is_pinching'] = True
            for shape in shapes:
                if not shape['is_snapped']:
                    dist_to_shape = math.hypot(smooth_cursor_pos[0] - shape['x'], smooth_cursor_pos[1] - shape['y'])
                    if dist_to_shape < SHAPE_SIZE:
                        held_shape = shape
                        break
        
        elif not is_pinching_now and pinch_state['is_pinching']:
            pinch_state['is_pinching'] = False
            if held_shape:
                target = held_shape['target_placeholder']
                dist_to_target = math.hypot(held_shape['x'] - target['x'], held_shape['y'] - target['y'])
                if dist_to_target < SNAP_DISTANCE:
                    held_shape['x'] = target['x']
                    held_shape['y'] = target['y']
                    held_shape['is_snapped'] = True
                    if all(s['is_snapped'] for s in shapes):
                        game_won = True
                held_shape = None
    else:
        if pinch_state['is_pinching']:
            pinch_state['is_pinching'] = False
            held_shape = None

    smooth_cursor_pos = (
        int(smooth_cursor_pos[0] * SMOOTHING_FACTOR + raw_cursor_pos[0] * (1 - SMOOTHING_FACTOR)),
        int(smooth_cursor_pos[1] * SMOOTHING_FACTOR + raw_cursor_pos[1] * (1 - SMOOTHING_FACTOR))
    )
    pinch_state['pos'] = smooth_cursor_pos

    if held_shape:
        held_shape['x'] = smooth_cursor_pos[0]
        held_shape['y'] = smooth_cursor_pos[1]

    # --- Drawing game elements on top of the frame ---
    for p in placeholders:
        draw_shape(frame, p, is_placeholder=True)
    for s in shapes:
        draw_shape(frame, s)
        
    cursor_color = COLORS['green_cursor'] if pinch_state['is_pinching'] else COLORS['yellow_cursor']
    cv2.circle(frame, pinch_state['pos'], 15, cursor_color, -1)
    cv2.circle(frame, pinch_state['pos'], 15, COLORS['white'], 2)

    cv2.putText(frame, "Pinch to grab, release to drop. Press 'q' to quit.", (20, SCREEN_HEIGHT - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)

    if game_won:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), COLORS['black'], -1)
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        cv2.putText(frame, "YOU WIN!", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2),
                    cv2.FONT_HERSHEY_TRIPLEX, 2, COLORS['green'], 3)
        cv2.putText(frame, "Press 'r' to play again.", (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['white'], 2)

    cv2.imshow('Gesture Puzzle Game', frame)

    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    if key == ord('r') and game_won:
        initialize_game()

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()