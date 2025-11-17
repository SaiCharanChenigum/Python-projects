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

#Live demo of this project is shown in this link : https://www.linkedin.com/posts/chenigumsaicharan_python-opencv-mediapipe-ugcPost-7374726023625498624-p0I7?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAADz3elUBUzp05GOoTRoquhmOvbwtfkQ9aV0
