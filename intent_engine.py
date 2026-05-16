from groq import Groq
from dotenv import load_dotenv
import os
import json
import re
from pathlib import Path

# 🔥 LOAD ENV VARIABLES
load_dotenv()

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ API KEY NOT FOUND")

client = Groq(api_key=api_key)


def understand_intent(user_input, state=None):

    # 🔥 DEFAULT STATE
    if state is None:
        state = {}

    # 🔥 IGNORE EMPTY INPUT
    if len(user_input.strip()) <= 1:
        return {}

    prompt = f"""
You are Zoro.

Zoro is an advanced AI laptop assistant.

Your ONLY job is to understand the REAL HUMAN INTENTION.

IMPORTANT:
- DO NOT generate clicks
- DO NOT generate actions
- DO NOT generate steps
- ONLY understand meaning

Return ONLY VALID JSON.
No markdown.
No explanation.
No extra text.

Current system state:
{json.dumps(state, indent=2)}

OUTPUT FORMAT:

{{
    "goal": "",
    "platform": "",
    "target": "",
    "query": "",
    "data": {{}}
}}

GOAL EXAMPLES:
- play_music
- play_video
- search_web
- open_app
- close_app
- create_folder
- open_folder
- search_file
- send_message
- type_text

EXAMPLES:

User: spotify pe arijit singh ke songs chala

{{
    "goal": "play_music",
    "platform": "spotify",
    "target": "arijit singh",
    "query": "arijit singh songs",
    "data": {{}}
}}

User: youtube pe sad songs chala

{{
    "goal": "play_music",
    "platform": "youtube",
    "target": "sad songs",
    "query": "sad songs",
    "data": {{}}
}}

User: create folder called notes in downloads

{{
    "goal": "create_folder",
    "platform": "file_system",
    "target": "downloads",
    "query": "",
    "data": {{
        "folder_name": "notes"
    }}
}}

User: downloads folder open kar

{{
    "goal": "open_folder",
    "platform": "file_system",
    "target": "Downloads",
    "query": "",
    "data": {{}}
}}

User: search python tutorial

{{
    "goal": "search_web",
    "platform": "browser",
    "target": "google",
    "query": "python tutorial",
    "data": {{}}
}}

User: open chrome

{{
    "goal": "open_app",
    "platform": "windows",
    "target": "chrome",
    "query": "",
    "data": {{}}
}}

User: whatsapp pe rohan ko hello bhej

{{
    "goal": "send_message",
    "platform": "whatsapp",
    "target": "rohan",
    "query": "hello",
    "data": {{}}
}}

User: software parts folder open kar

{{
    "goal": "open_folder",
    "platform": "file_system",
    "target": "Software Parts",
    "query": "",
    "data": {{}}
}}

User: {user_input}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an advanced AI intent understanding engine."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        print("\n🧠 RAW INTENT:\n")
        print(result)

        # 🔥 REMOVE MARKDOWN
        if result.startswith("```"):
            result = (
                result
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # 🔥 EXTRACT JSON OBJECT
        match = re.search(r'\{.*\}', result, re.DOTALL)

        if not match:
            print("❌ No JSON detected")
            return {}

        cleaned = match.group(0)

        # 🔥 CONVERT TO PYTHON DICT
        intent = json.loads(cleaned)

        print("\n✅ CLEANED INTENT:\n")
        print(json.dumps(intent, indent=4))

        return intent

    except Exception as e:
        print("❌ Intent Engine Error:", e)
        return {}