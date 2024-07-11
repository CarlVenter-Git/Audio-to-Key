import concurrent.futures
import sounddevice as sd
import numpy as np
import keyboard
import pygetwindow as gw
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import asyncio

# Variable for Threshold. Default sound level threshold
threshold = 100
# Default Key to press, variable can be changed
key_to_press = 'l'
# Selected window title, can be changed
selected_window_title = None
# Global variable to keep track of the audio stream
audio_stream = None
# Initialize the recognizer
recognizer = sr.Recognizer()

def is_game_focused(game_title):
    if game_title:
        window = gw.getWindowsWithTitle(game_title)
        return window and window[0].isActive
    return False

# Callback function to process audio input
def audio_callback(indata, frames, time, status):
    global threshold, key_to_press, selected_window_title
    volume_norm = np.linalg.norm(indata) * 10
    #print(volume_norm)  # Optional: Print volume for debugging
    if volume_norm > threshold and is_game_focused(selected_window_title):
        print("Loud sound detected!")
        keyboard.press(key_to_press)       
    
async def recognise_words():
    def recognize_speech_from_mic(recognizer, microphone):
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                print(f"Recognized speech: {text}")
                # Check if the recognized speech matches a command
                if "hello" in text.lower():
                    keyboard.press("m")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))   

    # Use ThreadPoolExecutor to run the blocking function in a separate thread
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(recognize_speech_from_mic, recognizer, sr.Microphone())
        return await asyncio.wrap_future(future)  # Convert Future to asyncio Future and await it

# Main function to start listening
def listen_to_microphone():
    global audio_stream
    if not audio_stream:
        audio_stream = sd.InputStream(callback=audio_callback)
        audio_stream.start()
        print("Started listening")
    asyncio.run(recognise_words())

# Function to stop listening
def stop_listening():
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
        audio_stream = None
        print("Stopped listening")

def select_input_device():
    devices = sd.query_devices()
    print("Select input device:")
    for i, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            print(f"{i}: {device['name']}")
        
    return devices[int(input())]

# Function to update the Key
def update_key(event):
    global key_to_press
    key_to_press = key_entry.get()
    print(f"Key to press updated to: {key_to_press}")

# Function to update the threshold
def update_threshold(event):
    global threshold
    try:
        threshold = float(threshold_entry.get())
        print(f"Threshold updated to: {threshold}")
    except ValueError:
        print("Invalid threshold value")

# Function to update the application this program is using.
def update_window(event):
    global selected_window_title
    selected_window_title = window_var.get()
    print(f"Selected window updated to: {selected_window_title}")

# Function to create and display the GUI
def create_gui():
    root = tk.Tk()
    root.title("Scream Dodge Settings")

    # Key entry
    tk.Label(root, text="Virtual Keybind:").grid(row=0, column=0)
    global key_entry
    key_entry = tk.Entry(root)
    key_entry.grid(row=0, column=1)
    key_entry.bind("<Return>", update_key)

    # Threshold entry
    tk.Label(root, text="Volume threshold:").grid(row=1, column=0)
    global threshold_entry
    threshold_entry = tk.Entry(root)
    threshold_entry.grid(row=1, column=1)
    threshold_entry.bind("<Return>", update_threshold)

    # Window dropdown
    tk.Label(root, text="Select Application:").grid(row=2, column=0)
    global window_var
    window_var = tk.StringVar(root)
    windows = gw.getAllTitles()
    window_menu = ttk.Combobox(root, textvariable=window_var)
    window_menu['values'] = windows
    window_menu.grid(row=2, column=1)
    window_menu.bind("<<ComboboxSelected>>", update_window)

    # Start button
    start_button = tk.Button(root, text="Start Screaming", command=listen_to_microphone)
    start_button.grid(row=3, column=0)

    # Stop button
    stop_button = tk.Button(root, text="Stop Screaming", command=stop_listening)
    stop_button.grid(row=3, column=1)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
