#Project: Automatic Screen Brightness Control Using Ambient Light Detection

#Description:

#This project implements an intelligent screen brightness controller for laptops
#using the built-in webcam as a real-time ambient light sensor. Instead of relying
#on hardware ALS (Ambient Light Sensor), the system estimates environmental lighting
#conditions by analyzing video frames from the camera.

#How It Works:

#1. Captures live video from the webcam.
#2. Converts each frame to grayscale and calculates the average pixel intensity.
#3. Maps this calculated 'lux' value to a realistic screen brightness percentage.
#4. Smoothly adjusts the laptop’s screen brightness through the
 #  `screen_brightness_control` module.
#5. Includes stability logic to prevent rapid flickering by applying a threshold
   #before updating brightness.

#Key Features:

#- Real-time brightness adjustment based on environment lighting.
#- Works on laptops without dedicated light sensors.
#- Efficient grayscale analysis for fast performance.
#- Prevents unnecessary brightness changes using differential thresholding.
#- Simple, compact, and hardware-independent implementation.

#Use Cases:

#- Power-saving brightness automation
#- Eye comfort during long laptop usage
#- Adaptive brightness for coding, studying, or multimedia use

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
