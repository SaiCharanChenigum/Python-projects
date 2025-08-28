import cv2
import mediapipe as mp
import pyautogui

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # Only 1 hand needed
mp_draw = mp.solutions.drawing_utils

# Function to detect gesture
def is_jump_gesture(landmarks):
    point4 = landmarks[4]
    point6 = landmarks[6]
    distance = ((point4.x - point6.x) ** 2 + (point4.y - point6.y) ** 2) ** 0.5
    return distance < 0.06 # Adjust if needed

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Webcam not accessible")
    exit()

space_pressed = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            hand_label = hand_info.classification[0].label
            if hand_label == "Right":
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if is_jump_gesture(hand_landmarks.landmark):
                    if not space_pressed:
                        print("Jump (spacebar pressed)")
                        pyautogui.keyDown('space')
                        space_pressed = True
                else:
                    if space_pressed:
                        print("Release (spacebar released)")
                        pyautogui.keyUp('space')
                        space_pressed = False

    cv2.imshow("Dino Jump Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
