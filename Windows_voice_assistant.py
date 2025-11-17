import speech_recognition as sr
from datetime import datetime
import threading
import pyautogui
import os
import webbrowser
import screen_brightness_control as sbc
import psutil
import time
import pygetwindow as gw
import uuid
import ctypes
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

listening_for_command = True
activate_sound_played = False

def play_sound_effect(filename):
    try:
        sound = AudioSegment.from_file(filename)
        threading.Thread(target=play, args=(sound,)).start()
    except Exception as e:
        print(f"Failed to play sound {filename}: {e}")

def speak(text, block=False):
    filename = f"temp_speak_{uuid.uuid4()}.mp3"
    try:
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
        tts.save(filename)
        audio = AudioSegment.from_mp3(filename)
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 1.2)
        }).set_frame_rate(audio.frame_rate)

        if block:
            play(audio)
        else:
            threading.Thread(target=play, args=(audio,)).start()
    except Exception as e:
        print(f"Error in speak: {e}")
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as cleanup_e:
                print(f"Error during cleanup: {cleanup_e}")

def get_battery_percentage():
    battery = psutil.sensors_battery()
    return battery.percent

def check_battery_status():
    while True:
        battery_percentage = get_battery_percentage()
        if battery_percentage <= 15:
            speak("Battery is getting low, charge the laptop.")
        time.sleep(60)

def get_current_time():
    now = datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}"

def set_brightness(level):
    try:
        level = int(level)
        if 1 <= level <= 100:
            sbc.set_brightness(level)
            speak(f"Brightness set to {level} percent")
        else:
            speak("Please specify a brightness level between 1 and 100")
    except ValueError:
        speak("Sorry, I couldn't understand the brightness level.")


def get_active_window_title():
    active_window = gw.getActiveWindow()
    return active_window.title if active_window else None


def is_youtube_active():
    active_window_title = get_active_window_title()
    return active_window_title and "YouTube" in active_window_title


def execute_command(command):
    global listening_for_command

    if "what is the time now" in command:
        speak(get_current_time())

    elif "change window" in command:
        pyautogui.hotkey('alt', 'tab')

    elif "lock my pc" in command:
        os.system('rundll32.exe user32.dll,LockWorkStation')

    elif "go to sleep" in command:
        os.system('rundll32.exe powrprof.dll,SetSuspendState Sleep')

    elif "shut down my pc" in command:
        listening_for_command = False
        speak("Are you sure you want to shut down your PC? Say yes to confirm or no to cancel.", block=True)
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for shutdown confirmation...")
            try:
                audio = recognizer.listen(source, timeout=5)
                confirmation = recognizer.recognize_google(audio).lower()
                if "yes" in confirmation:
                    speak("Shutting down your PC now.", block=False)
                    os.system('shutdown /s /f /t 0')
                elif "no" in confirmation:
                    speak("Shutdown cancelled.", block=False)
                else:
                    speak("I didn't understand your response. Shutdown cancelled.", block=False)
            except sr.WaitTimeoutError:
                speak("No response received. Shutdown cancelled.", block=False)
            except sr.UnknownValueError:
                speak("Could not understand audio. Shutdown cancelled.", block=False)
            except sr.RequestError as e:
                speak(f"Could not request results; {e}. Shutdown cancelled.", block=False)
            finally:
                listening_for_command = True
        return

    elif "what is my battery percentage" in command or "what's my battery percentage" in command:
        battery_percentage = get_battery_percentage()
        speak(f"Your battery is at {battery_percentage} percent.")

    elif "open chrome" in command:
        os.startfile(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

    elif "take a screenshot" in command:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot = pyautogui.screenshot()
        screenshot.save(f'C:\\Users\\cheni\\Pictures\\Screenshots\\screenshot_{timestamp}.png')
        speak("Screenshot taken.")

    elif "open control centre" in command:
        pyautogui.hotkey('win', 'a')
    
    elif "open control centre" in command:
        pyautogui.hotkey('win','a')

    elif "open settings" in command:
        pyautogui.hotkey('win', 'i')

    elif "show desktop" in command:
        pyautogui.hotkey('win', 'd')

    elif "close the window" in command:
        active_window = gw.getActiveWindow()
        if active_window:
            active_window.close()
            speak("Active window closed.")
        else:
            speak("No active window detected.")

    elif "play the video" in command or "pause the video" in command or "stop the video" in command:
        if is_youtube_active():
            pyautogui.press('playpause')
            speak("Video toggled.", block=False)
        else:
            speak("YouTube is not currently the active window.", block=False)

    elif "set brightness to" in command:
        brightness_level = command.split("set brightness to")[1].strip()
        brightness_value = ''.join(filter(str.isdigit, brightness_level))
        set_brightness(brightness_value)

    elif "search" in command:
        try:
            search_text = command.split("search")[1].split("on")[0].strip()
            website = command.split("on")[1].strip()

            if "youtube" in website:
                url = f"https://www.youtube.com/results?search_query={search_text}"
            elif "wikipedia" in website:
                url = f"https://en.wikipedia.org/wiki/{search_text.replace(' ', '_')}"
            elif "google" in website:
                url = f"https://www.google.com/search?q={search_text}"
            else:
                url = f"https://www.google.com/search?q={search_text}"

            webbrowser.open(url)
            speak(f"Searching {search_text} on {website}")

        except Exception as e:
            speak(f"Sorry, I couldn't understand the search command. Error: {e}")

def listen_and_execute():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        if not listening_for_command:
            time.sleep(0.1)
            continue

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for trigger: hello Windows...")
            try:
                audio = recognizer.listen(source, timeout=5)
                phrase = recognizer.recognize_google(audio).lower()
                print(f"Heard: {phrase}")
                if "hello windows" in phrase:
                    play_sound_effect("activate.mp3")
                    session_start = time.time()
                    last_command_time = time.time()
                    while time.time() - last_command_time < 120:
                        print("Listening for command...")
                        try:
                            audio2 = recognizer.listen(source, timeout=15)
                            command = recognizer.recognize_google(audio2).lower()
                            print(f"Command: {command}")
                            execute_command(command)
                            last_command_time = time.time()  # reset timeout after each command
                        except sr.WaitTimeoutError:
                            print("No command detected within 15 seconds.")
                        except (sr.UnknownValueError, sr.RequestError) as e:
                            print(f"Command recognition error: {e}")
                    play_sound_effect("deactivate.mp3")
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except sr.RequestError as e:
                print(f"Google API error: {e}")
                speak("Sorry, there was a problem with the speech recognition service.", block=False)
if __name__ == "__main__":
    battery_thread = threading.Thread(target=check_battery_status, daemon=True)
    battery_thread.start()
    command_thread = threading.Thread(target=listen_and_execute)
    command_thread.start()
    command_thread.join()
