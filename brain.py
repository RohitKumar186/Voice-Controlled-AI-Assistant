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
You are Zoro (bro), a smart and helpful voice assistant for Rohit on Windows laptop.

Understand natural spoken commands and convert them into simple executable actions.

STRICT RULES:
- Return ONLY valid JSON array [] 
- No explanations, no extra text, no markdown
- Use ONLY the allowed actions
- For "open app search ABC" in WhatsApp → open_app + hotkey Ctrl+F + type_text
- For "open app and type ABC" → open_app + type_text
- For "open windows search XYZ" → open_search + type_text + press_enter

Allowed actions:
- open_app          → {{"action": "open_app", "app": "name"}}
- open_website      → {{"action": "open_website", "url": "https://..."}}
- open_search       → {{"action": "open_search"}}
- type_text         → {{"action": "type_text", "text": "exact text"}}
- press_enter       → {{"action": "press_enter"}}
- hotkey            → {{"action": "hotkey", "keys": ["ctrl", "f"]}}
- click             → {{"action": "click"}}

Examples (follow exactly):

User: open whatsapp
[{{"action": "open_app", "app": "whatsapp"}}]

User: open whatsapp search mehar
[
  {{"action": "open_app", "app": "whatsapp"}},
  {{"action": "hotkey", "keys": ["ctrl", "f"]}},
  {{"action": "type_text", "text": "mehar"}}
]

User: open whatsapp search mehar type hello then press enter
[
  {{"action": "open_app", "app": "whatsapp"}},
  {{"action": "hotkey", "keys": ["ctrl", "f"]}},
  {{"action": "type_text", "text": "mehar"}},
  {{"action": "type_text", "text": "hello"}},
  {{"action": "press_enter"}}
]

User: open notepad and type hello how are you
[
  {{"action": "open_app", "app": "notepad"}},
  {{"action": "type_text", "text": "hello how are you"}}
]

User: open command prompt type dir then press enter
[
  {{"action": "open_app", "app": "cmd"}},
  {{"action": "type_text", "text": "dir"}},
  {{"action": "press_enter"}}
]

User: open windows search multisim
[
  {{"action": "open_search"}},
  {{"action": "type_text", "text": "multisim"}},
  {{"action": "press_enter"}}
]

User: open chrome search technical
[
  {{"action": "open_app", "app": "chrome"}},
  {{"action": "open_website", "url": "https://www.google.com/search?q=technical"}}
]

User: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict JSON command parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content
        print("RAW LLM OUTPUT:", result)

        cleaned = result.strip()
        # After cleaned = result.strip()
        cleaned = re.sub(r'^.*?($$   .*   $$)', r'\1', cleaned, flags=re.DOTALL)  # extract JSON array

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
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict JSON command parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content
        print("RAW LLM OUTPUT:", result)

        cleaned = result.strip()

        # Remove markdown code blocks if any
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1].strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        # Extract only the JSON array safely
        import re
        match = re.search(r'\[[\s\S]*?\]', cleaned)
        if match:
            cleaned = match.group(0)

        print("CLEANED OUTPUT:", cleaned)

        # Parse the JSON
        actions = json.loads(cleaned)

        # Ensure it's a list
        if isinstance(actions, dict):
            actions = [actions]

        return actions

    except Exception as e:
        print("Groq Error:", e)
        if 'result' in locals():
            print("RAW LLM OUTPUT was:", result)
        return []