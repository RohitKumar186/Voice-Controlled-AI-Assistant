import pyautogui
import easyocr
import cv2
import numpy as np
import time

# 🔥 LOAD OCR READER
reader = easyocr.Reader(['en'], gpu=False)


# 📸 TAKE SCREENSHOT
def capture_screen():

    screenshot = pyautogui.screenshot()

    image = np.array(screenshot)

    # Convert RGB → BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


# 🔍 FIND TEXT ON SCREEN
def find_text(text_to_find):

    image = capture_screen()

    results = reader.readtext(image)

    print("\n🔍 OCR RESULTS:\n")

    for result in results:

        bbox, detected_text, confidence = result

        print(detected_text)

        # 🔥 MATCH TEXT
        if text_to_find.lower() in detected_text.lower():

            x = int((bbox[0][0] + bbox[2][0]) / 2)
            y = int((bbox[0][1] + bbox[2][1]) / 2)

            print(f"\n✅ FOUND: {detected_text}")
            print(f"📍 Coordinates: {x}, {y}")

            return (x, y)

    print(f"\n❌ Text '{text_to_find}' not found")

    return None


# 🖱️ CLICK TEXT
def click_text(text):

    location = find_text(text)

    if not location:
        return False

    x, y = location

    pyautogui.click(x, y)

    print(f"\n🖱️ Clicked on: {text}")

    return True
# 👀 DOUBLE CLICK TEXT

def double_click_text(text):

    location = find_text(text)

    if not location:
        return False

    x, y = location

    pyautogui.doubleClick(x, y)

    print(f"\n🖱️ Double clicked on: {text}")

    return True