from matplotlib.pyplot import step
from vision import click_text, double_click_text

from intent_engine import understand_intent
from planner import create_plan
from playsound import playsound
import speech_recognition as sr
import pyautogui
import time
import os
import random
import datetime
import asyncio
import edge_tts
import uuid
import urllib.parse



pyautogui.FAILSAFE = True

recognizer = sr.Recognizer()

STATE = {
    "current_app": "",
    "current_website": "",
    "last_command": "",
    "last_query": "",
    "history": []
}

def update_state(step):
    action = step.get("action")

    # 🔥 Track current app
    if action == "open_app":
        STATE["current_app"] = step.get("app")

    # 🌐 Track website
    if action == "open_website":
        url = step.get("url", "")

        if "youtube" in url:
            STATE["current_website"] = "youtube"
        elif "google" in url:
            STATE["current_website"] = "google"

    # 🔍 Track last search
    if action in ["search_web", "search_in_youtube"]:
        STATE["last_query"] = step.get("query")

    # 🧠 Save history
    STATE["history"].append(step)

def apply_rules(actions):
    print("Actions from LLM:", actions)
    # For now we let LLM decide directly (we will improve later if needed)
    return actions
# 🔥 CONTEXT MEMORY
CURRENT_APP = None

APP_PATHS = {
    "chrome": "start chrome",
    "notepad": "notepad",
    "task manager": "taskmgr",
    "calculator": "calc",
    "vscode": "code",
    "whatsapp": "start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "this pc": "explorer"
}
APP_PROCESS = {
    "chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "vscode": "Code.exe",
    "calculator": "Calculator.exe",
    "task manager": "Taskmgr.exe",
    "whatsapp": "WhatsApp.exe"
}

WAKE_WORDS = ["hey bro", "hi bro", "hello bro"]


# 🔊 SPEAK
async def async_speak(text, filename):
    communicate = edge_tts.Communicate(text, voice="en-IN-NeerjaNeural")
    await communicate.save(filename)


def speak(text):
    print("luffy:", text)
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    asyncio.run(async_speak(text, filename))

    try:
        playsound(filename)
    except:
        print("Error playing sound")


# 👋 GREETING
def greet_user():
    hour = datetime.datetime.now().hour

    if hour < 12:
        greetings = [
            "Good morning Rohit ☀️ ready to start?",
            "Morning! Let’s make today productive 🔥"
        ]
    elif hour < 18:
        greetings = [
            "Good afternoon Rohit 😎 what’s the plan?",
            "Hey! Hope your day is going great 👀"
        ]
    else:
        greetings = [
            "Working late huh Rohit 😏",
            "Good evening! Still grinding? 🔥"
        ]

    speak(random.choice(greetings))


# 🎤 LISTEN
def listen():
    with sr.Microphone() as source:
        print("Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.5

        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print("You:", command)
            return command.lower().strip()
        except:
            return ""

def handle_intent(intent):
    global CURRENT_APP

    if not intent:
        return False

    intent_type = intent.get("intent")

    # 🔥 PLAY VIDEO (YOUTUBE)
    if intent_type == "play_video":
        query = intent.get("query")

        speak(f"Playing {query} on YouTube")

        # Open YouTube
        os.system("start chrome https://www.youtube.com")
        time.sleep(5)

        # Search
        pyautogui.click(600, 200)   # search bar (may adjust)
        time.sleep(1)
        pyautogui.write(query)
        pyautogui.press("enter")

        time.sleep(3)

        # Click first video
        pyautogui.click(600, 200)

        return True

    # 🔥 SEARCH (GENERIC)
    elif intent_type == "search":
        query = intent.get("query")

        if not query:
            return False

        speak(f"Searching {query}")

        os.system(f"start chrome https://www.google.com/search?q={query}")
        return True

    # 🔥 OPEN APP
    elif intent_type == "open_app":
        app = intent.get("app")

        if not app:
            return False

        speak(f"Opening {app}")
        os.system(f"start {app}")
        return True

    # 🔥 CLOSE APP
    elif intent_type == "close_app":
        app = intent.get("app")

        if not app:
            return False

        speak(f"Closing {app}")
        os.system(f"taskkill /f /im {app}.exe")
        return True

    return False


# 🧠 EXECUTE
def execute(command):
    STATE["last_command"] = command 
    global CURRENT_APP

    if any(word in command for word in ["stop", "exit", "quit", "it's over", "its over"]):
        speak("Okay Rohit, stopping now")
        exit()

    # 🧠 UNDERSTAND USER INTENT
    intent = understand_intent(command, STATE)

    if not intent:
        speak("I could not understand your intention")
        return

    print("\n🧠 INTENT:")
    print(intent)

# 🔥 CREATE EXECUTION PLAN
    actions = create_plan(intent)

    print("\n📋 EXECUTION PLAN:")
    print(actions)

    if not actions:
        speak("I don't know how to do that yet")
        return

    if not actions:
        speak("I didn’t understand that properly 🤔")
        return

    valid_actions = [
    "open_app",
    "close_app",
    "search_web",
    "type_text",
    "press_enter",
    "press_key",
    "hotkey",
    "open_search",
    "open_website",
    "click"
    "wait",
    "create_folder",
    "click_text",
    "double_click_text"
]

    # 🔥 CLEAN INVALID ACTIONS
    cleaned_actions = []
    for step in actions:
        if isinstance(step, dict) and step.get("action") in valid_actions:
            cleaned_actions.append(step)
        else:
            print("⚠️ Ignored invalid step:", step)

    # 🔥 EXECUTE CLEANED ACTIONS
    for step in cleaned_actions:
        update_state(step) 
        print("Action:", step)

        action_type = step.get("action")

        # 🔥 OPEN APP
        if action_type == "open_app":
            app = step.get("app")

            if not app:
                print("⚠️ No app provided")
                continue

            CURRENT_APP = app
            speak(f"Opening {app}")

            if app in APP_PATHS:
                os.system(APP_PATHS[app])
            else:
                os.system(f"start {app}")

            time.sleep(6)
            if app == "whatsapp":
                time.sleep(2)   # extra time for WhatsApp to load

        # 🌐 SEARCH
        elif action_type == "search_web":
             query = step.get("query")

             if not query:
                 print("⚠️ No query provided")
                 continue

    # 🔥 WHATSAPP SEARCH
             if CURRENT_APP == "whatsapp":
                 speak(f"Searching {query} in WhatsApp")
                 pyautogui.hotkey("ctrl", "f")
                 time.sleep(1)
                 pyautogui.write(query, interval=0.05)
                 pyautogui.press("enter")

    # 🔥 THIS PC SEARCH (IMPORTANT FIX)
             elif CURRENT_APP == "this pc":
                 speak(f"Searching {query} in File Explorer")
                 pyautogui.hotkey("ctrl", "f")
                 time.sleep(1)
                 pyautogui.write(query, interval=0.05)

    # 🌐 DEFAULT → GOOGLE
             else:
                 speak(f"Searching {query}")
                 encoded_query = urllib.parse.quote(query)
                 os.system(f"start chrome https://www.google.com/search?q={encoded_query}")

        # ⌨️ TYPE TEXT
        elif action_type == "type_text":
            text = step.get("text") or step.get("input")

            if not text:
                print("⚠️ No text provided")
                continue

            speak(f"Typing {text}")
            time.sleep(1)
            pyautogui.write(text, interval=0.05)

        # ⏎ ENTER
        elif action_type == "press_enter":
            speak("Pressing enter")
            time.sleep(1)
            pyautogui.press("enter")

        # 🔥 SINGLE KEY
        elif action_type == "press_key":
            key = step.get("key")

            if not key:
                print("⚠️ No key provided")
                continue

            speak(f"Pressing {key}")
            pyautogui.press(key)

        # ⏳ WAIT
        elif action_type == "wait":

            seconds = step.get("seconds", 1)
            print(f"Waiting {seconds} seconds")
            time.sleep(seconds)

        # 🔥 HOTKEY
        elif action_type == "hotkey":
            keys = step.get("keys")

            if not keys:
                print("⚠️ No keys provided")
                continue

            speak(f"Pressing {' + '.join(keys)}")
            pyautogui.hotkey(*keys)

        elif action_type == "close_app":
            app = step.get("app")

            if not app:
                print("⚠️ No app provided")
                continue

            process = APP_PROCESS.get(app, f"{app}.exe")

            speak(f"Closing {app}")
            os.system(f"taskkill /f /im {process}")

        # 📁 CREATE FOLDER
        elif action_type == "create_folder":

            path = step.get("path", "")
            folder_name = step.get("folder_name", "New Folder")

            try:

                if path.lower() == "downloads":
                    base_path = os.path.join(os.path.expanduser("~"), "Downloads")

                elif path.lower() == "desktop":
                    base_path = os.path.join(os.path.expanduser("~"), "Desktop")

                else:
                    base_path = path

                    full_path = os.path.join(base_path, folder_name)
                    os.makedirs(full_path, exist_ok=True)
                    speak(f"Folder {folder_name} created successfully")

            except Exception as e:
                print("Folder Error:", e)
                speak("Failed to create folder")

        # 🔍 OPEN WINDOWS SEARCH
        elif action_type == "open_search":
            speak("Opening search")
            pyautogui.press("win")
            time.sleep(1)

# 🌐 OPEN WEBSITE
        elif action_type == "open_website":
            url = step.get("url")

            if not url:
                print("⚠️ No URL provided")
                continue
            if not url.startswith("http"):
                url = f"https://{url}.com"

            speak("Opening website")
            os.system(f"start chrome {url}")
            time.sleep(3)

# 🖱️ CLICK
        elif action_type == "click":
            x = step.get("x", 500)
            y = step.get("y", 300)

            speak("Clicking")
            pyautogui.click(x, y)
        
        # 👀 CLICK TEXT ON SCREEN
        elif action_type == "click_text":

            text = step.get("text", "")

            if not text:
                continue

            speak(f"Looking for {text}")

            success = click_text(text)

            if not success:
                speak(f"I could not find {text}")
        
        # 👀 DOUBLE CLICK TEXT
        elif action_type == "double_click_text":

            text = step.get("text", "")

            if not text:
                continue

            speak(f"Opening {text}")

            success = double_click_text(text)

            if not success:
                speak(f"I could not find {text}")

        elif action_type == "focus_search":
            speak("Focusing search")
            time.sleep(1)

    # 🔥 BEST METHOD (universal)
            pyautogui.hotkey("ctrl", "l")   # focus address bar
            time.sleep(5)
        

# 🚀 START
print("Zoro is running...")

while True:
    text = listen()

    if text.startswith(tuple(WAKE_WORDS)):
        greet_user()

        while True:
            command = listen()

            if command == "":
                continue

            if "sleep" in command or "stop listening" in command:
                speak("Going back to sleep")
                break

            
            execute(command)
    print("Going back to sleep...\n")

