from groq import Groq
from dotenv import load_dotenv
import os
import json
import re
from pathlib import Path

# 🔥 LOAD ENV
load_dotenv()

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


def create_plan(intent, state=None):

    if not intent:
        return []

    if state is None:
        state = {}

    prompt = f"""
You are an advanced AI planner.

Your job:
Convert user intention into executable computer actions.

IMPORTANT:
Return ONLY valid JSON array.

No explanation.
No markdown.
No extra text.

You are controlling a Windows laptop.

Current State:
{json.dumps(state, indent=2)}

USER INTENT:
{json.dumps(intent, indent=2)}

ALLOWED ACTIONS:

- open_app
{{"action":"open_app","app":"chrome"}}

- open_website
{{"action":"open_website","url":"https://google.com"}}

- type_text
{{"action":"type_text","text":"hello"}}

- press_enter
{{"action":"press_enter"}}

- hotkey
{{"action":"hotkey","keys":["ctrl","l"]}}

- click
{{"action":"click"}}

- wait
{{"action":"wait","seconds":2}}

- create_folder
{{"action":"create_folder","path":"downloads","folder_name":"movies"}}

- click_text
{{"action":"double_click_text","text":"Downloads"}}

- double_click_text
{{"action":"double_click_text","text":"Downloads"}}

RULES:
- Think step-by-step
- Generate smart plans
- Use minimum actions
- Be dynamic
- Understand app/platform automatically
- If music/video requested → use browser/youtube unless specified
- If folder requested → use create_folder
- If search requested → use browser
- NEVER explain anything

EXAMPLES:

Intent:
{{
  "goal":"send_message",
  "platform":"whatsapp",
  "target":"rohan",
  "query":"hello"
}}

Output:
[
  {{
    "action":"open_app",
    "app":"whatsapp"
  }},
  {{
    "action":"wait",
    "seconds":4
  }},
  {{
    "action":"hotkey",
    "keys":["ctrl","f"]
  }},
  {{
    "action":"type_text",
    "text":"rohan"
  }},
  {{
    "action":"press_enter"
  }},
  {{
    "action":"wait",
    "seconds":1
  }},
  {{
    "action":"type_text",
    "text":"hello"
  }},
  {{
    "action":"press_enter"
  }}
]

Intent:
{{
  "goal":"play_music",
  "platform":"youtube",
  "query":"sad songs"
}}

Output:
[
  {{
    "action":"open_website",
    "url":"https://www.youtube.com/results?search_query=sad+songs"
  }},
  {{
    "action":"wait",
    "seconds":3
  }},
  {{
    "action":"click"
  }}
]

Intent:
{{
  "goal":"create_folder",
  "platform":"file_system",
  "target":"downloads",
  "data": {{
    "folder_name":"notes"
  }}
}}

Output:
[
  {{
    "action":"create_folder",
    "path":"downloads",
    "folder_name":"notes"
  }}
]

Intent:
{{
  "goal":"open_app",
  "target":"chrome"
}}

Output:
[
  {{
    "action":"open_app",
    "app":"chrome"
  }}
]

Intent:
{{
  "goal":"search_web",
  "query":"python tutorial"
}}

Output:
[
  {{
    "action":"open_website",
    "url":"https://www.google.com/search?q=python+tutorial"
  }}

Intent:
{{
  "goal":"open_folder",
  "target":"software parts"
}}

Output:
[
  {{
    "action":"click_text",
    "text":"Software Parts"
  }}
]

]"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI planning engine."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        print("\n🧠 RAW PLAN:\n")
        print(result)

        # 🔥 REMOVE MARKDOWN
        if result.startswith("```"):
            result = (
                result
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # 🔥 EXTRACT JSON ARRAY
        match = re.search(r'\[.*\]', result, re.DOTALL)

        if not match:
            print("❌ No JSON array found")
            return []

        cleaned = match.group(0)

        plan = json.loads(cleaned)

        print("\n✅ CLEAN PLAN:\n")
        print(json.dumps(plan, indent=4))

        return plan

    except Exception as e:
        print("Planner Error:", e)
        return []