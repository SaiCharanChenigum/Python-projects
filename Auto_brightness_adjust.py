import cv2
import numpy as np
import screen_brightness_control as sbc

def calculate_lux(grayscale_frame):
    avg_brightness = np.mean(grayscale_frame)
    return avg_brightness * 1.2

def map_lux_to_brightness(lux, min_brightness=10, max_brightness=100):
    brightness = np.clip(lux / 255 * max_brightness, min_brightness, max_brightness)
    return int(brightness)

def adjust_brightness(brightness):
    sbc.set_brightness(brightness)
    print(f"Adjusted Brightness: {brightness}%")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

try:
    previous_brightness = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lux = calculate_lux(grayscale_frame)
        print(f"Lux Intensity: {lux:.2f}")
        brightness = map_lux_to_brightness(lux)

        if previous_brightness is None or abs(previous_brightness - brightness) > 2:
            adjust_brightness(brightness)
            previous_brightness = brightness

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
