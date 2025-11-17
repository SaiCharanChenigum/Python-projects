# Project: Hand-Gesture Based Game Controller (Hill Climb Racing Game)

# Description:
# ------------
# This project implements a real-time hand-gesture recognition system that allows
# the user to control the "Gas" and "Brake" actions of the game *Hill Climb Racing*
# without using the keyboard. Both actions are triggered using a simple hand pinch
# gesture detected via the webcam.
#
# How It Works:
# -------------
# 1. MediaPipe Hands detects and tracks both hands (left and right) using the webcam.
# 2. The program checks for a "thumb–index finger pinch" gesture by measuring the
#    distance between the thumb tip (landmark 4) and the index finger tip (landmark 8).
# 3. When the gesture is detected:
#       - Left hand pinch  →  Press 'left arrow' (Brake)
#       - Right hand pinch →  Press 'right arrow' (Gas)
# 4. Releasing the gesture automatically releases the respective key.
# 5. The webcam feed displays real-time hand landmarks for debugging and visualization.
#
# Key Features:
# -------------
# - Hands-free control for racing games
# - Real-time gesture tracking using MediaPipe
# - No additional hardware required — only a webcam
# - Smooth key simulation using `pyautogui`
# - Designed for quick demos, CV projects, and interactive game control experiments
#
# Technical Highlights:
# ---------------------
# - MediaPipe: High-accuracy hand landmark detection
# - OpenCV: Real-time video capture & frame processing
# - PyAutoGUI: Simulated keyboard input for game control
# - Gesture recognition based on landmark distance thresholds

# Controls:
# ---------
# - Right hand pinch  → Gas (Right arrow key)
# - Left hand pinch   → Brake (Left arrow key)
# - Press 'q' to exit the program
#
# Live Demo:
# ----------
# A demonstration video of this project is available on my LinkedIn:
# https://www.linkedin.com/posts/chenigumsaicharan_python-opencv-mediapipe-ugcPost-7374726023625498624-p0I7

print("Script started...")
import cv2
import mediapipe as mp
import pyautogui

print("Starting hand control program...")

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# Function to detect thumb and index finger pinch
def is_thumb_index_pinch(landmarks):
    thumb_tip = landmarks[4]
    index_finger_tip = landmarks[8]
    if abs(thumb_tip.x - index_finger_tip.x) < 0.05 and abs(thumb_tip.y - index_finger_tip.y) < 0.05:
        return True
    return False

# Start the webcam capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Webcam not accessible")
    exit()

print("Webcam successfully opened")

gas_pressed = False
brake_pressed = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    else:
        print("Frame grabbed")

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_label = hand_info.classification[0].label

            if is_thumb_index_pinch(hand_landmarks.landmark):
                if hand_label == "Left" and not brake_pressed:
                    print("Brake pressed")
                    pyautogui.keyDown('left')
                    brake_pressed = True
                elif hand_label == "Right" and not gas_pressed:
                    print("Gas pressed")
                    pyautogui.keyDown('right')
                    gas_pressed = True
            else:
                if hand_label == "Left" and brake_pressed:
                    print("Brake released")
                    pyautogui.keyUp('left')
                    brake_pressed = False
                if hand_label == "Right" and gas_pressed:
                    print("Gas released")
                    pyautogui.keyUp('right')
                    gas_pressed = False

    cv2.imshow("Hill Climb Racing Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
print("Program ended.")

