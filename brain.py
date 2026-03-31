from dotenv import load_dotenv
 # This loads the variables from .env
from groq import Groq
import json
import re 
import os
from pathlib import Path
load_dotenv()
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

# Debugging: Run karte hi ye print karega agar key nahi mili
if not api_key:
    print(f"ERROR: .env file not found at {env_path}")
    # Isse check ho jayega ki Python kahan file dhoond raha hai
else:
    print("Success: API Key loaded!")

client = Groq(api_key=api_key)
def understand_command(user_input):

    if len(user_input.split()) <= 1:
        print("Ignoring short command")
        return []

    prompt = f"""
    Convert the user command into a sequence of executable actions.

    STRICT RULES:
    - Only return valid JSON list []
    - No explanation
- Each step must have "action"

Allowed actions:
- open_app
- open_search
- open_website
- type_text
- press_enter
- press_key
- hotkey
- click

Examples:

User: open whatsapp
[{{"action": "open_app", "app": "whatsapp"}}]

User: search free fire
[
  {{"action": "open_search"}},
  {{"action": "type_text", "text": "free fire"}},
  {{"action": "press_enter"}}
]

User: open youtube and play song
[
  {{"action": "open_website", "url": "https://youtube.com"}},
  {{"action": "type_text", "text": "song"}},
  {{"action": "press_enter"}}
]

User: open notepad and type hello
[
  {{"action": "open_app", "app": "notepad"}},
  {{"action": "type_text", "text": "hello"}}
]

User: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a strict JSON command parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content
        print("RAW LLM OUTPUT:", result)

        cleaned = result.strip()

        # 🔥 REMOVE MARKDOWN
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # 🔥 TRY DIRECT PARSE
        try:
            actions = json.loads(cleaned)
        except:
            # 🔥 FALLBACK → extract first JSON
            match = re.search(r'\[.*?\]', cleaned, re.DOTALL)

            if not match:
                print("⚠️ No valid JSON found")
                return []

            try:
                actions = json.loads(match.group(0))
            except Exception as e:
                print("JSON error:", e)
                return []

        # 🔥 ENSURE LIST
        if isinstance(actions, dict):
            actions = [actions]

        return actions

    except Exception as e:
        print("Groq Error:", e)
        return []



# PHASE 6

def understand_intent(user_input):

    prompt = f"""
You are an AI that understands user intent.

Convert user command into structured JSON.

Rules:
- Only return JSON (no explanation)
- Identify intent clearly

Intents:
- open_app
- search
- play_video
- type
- close_app

Examples:

User: open chrome
{{"intent": "open_app", "app": "chrome"}}

User: open youtube and play hindi song
{{"intent": "play_video", "platform": "youtube", "query": "hindi song"}}

User: search python tutorial
{{"intent": "search", "query": "python tutorial"}}

User: close chrome
{{"intent": "close_app", "app": "chrome"}}

User: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an intent detection AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content
        print("INTENT RAW:", result)

        cleaned = result.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        intent = json.loads(cleaned)

        return intent

    except Exception as e:
        print("Intent Error:", e)
        return {}