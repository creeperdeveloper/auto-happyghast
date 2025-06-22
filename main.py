import pytesseract
import re
from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui
import time
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
tolerance = 1
sleep_interval = 0.2

def get_xyz_from_screen():
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(binary)
    match = re.search(r'(-?\d+)[,\s]+(-?\d+)[,\s]+(-?\d+)', text)
    if match:
        return tuple(map(int, match.groups()))
    return None

def rise_to_height(target_y):
    print(f"Phase 1: Rising to Y >= {target_y}")
    last_coords = None
    while last_coords is None:
        last_coords = get_xyz_from_screen()
        print("Waiting for coordinate read...")
        time.sleep(0.5)

    x, y, z = last_coords
    while y < target_y:
        pyautogui.keyDown('space')
        time.sleep(0.3)
        pyautogui.keyUp('space')
        time.sleep(0.3)
        coords = get_xyz_from_screen()
        if coords:
            _, y, _ = coords
        else:
            y += 1
        print(f"Current Y: {y}")

def move_horizontal(target_x, target_z):
    print(f"Phase 2: Moving to X={target_x}, Z={target_z}")
    last_coords = None
    while last_coords is None:
        last_coords = get_xyz_from_screen()
        time.sleep(0.5)

    while True:
        current = get_xyz_from_screen()
        if current:
            last_coords = current
        x, y, z = last_coords

        dx, dz = target_x - x, target_z - z
        print(f"Current X:{x}, Z:{z} | ΔX:{dx}, ΔZ:{dz}")

        if abs(dx) <= tolerance and abs(dz) <= tolerance:
            print("Reached horizontal target.")
            break

        keys_pressed = []

        if dx > tolerance:
            pyautogui.keyDown('w'); keys_pressed.append('w'); x += 1
        elif dx < -tolerance:
            pyautogui.keyDown('s'); keys_pressed.append('s'); x -= 1
 
        if dz > tolerance:
            pyautogui.keyDown('d'); keys_pressed.append('d'); z += 1
        elif dz < -tolerance:
            pyautogui.keyDown('a'); keys_pressed.append('a'); z -= 1

        time.sleep(sleep_interval)

        for k in keys_pressed:
            pyautogui.keyUp(k)

        time.sleep(0.1)

def auto_navigate(x, y, z):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"Starting navigation to X={x}, Y={y}, Z={z}\n")
    time.sleep(1)
    time.sleep(1)
    time.sleep(1)

    move_horizontal(x, z)
    print("\nArrived at destination.")

# 実行
if __name__ == "__main__":
    try:
        tx = int(input("Target X: "))
        ty = int(input("Target Y: "))
        tz = int(input("Target Z: "))
        input("Press Enter to begin. Make sure Minecraft is active.")
        rise_to_height(100)
        auto_navigate(tx, ty, tz)
    except KeyboardInterrupt:
        print("Movement cancelled by user.")
