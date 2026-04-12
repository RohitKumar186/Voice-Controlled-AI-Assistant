# ⚔️ Zoro: LLM-Powered Voice Assistant
Zoro is a sophisticated Natural Language to Executable Action (NL2EA) framework. Unlike traditional assistants that rely on rigid regex patterns, 
Zoro utilizes Llama 3.3 (70B) via the Groq API to parse complex, multi-step human instructions into structured JSON action sequences for Windows automation.

 ## 🚀 Key Features
 
Intent-Aware Parsing: Understands nested commands like "Open WhatsApp, search for Mehar, and type 'See you at the hackathon'".
Contextual State Machine: Tracks the active application to determine if a "search" command should target a web browser, File Explorer, or a specific app's internal search.
Hybrid Automation: Combines os system calls for process management with PyAutoGUI for fine-grained GUI interaction (hotkeys, typing, clicking).
Neural TTS: High-fidelity, low-latency voice feedback powered by edge-tts.

## 🛠️ The Architecture

The system operates in a three-stage pipeline:
Perception: Speech-to-Text via SpeechRecognition captures the wake word ("Hey Bro") and the user command.
Cognition (brain.py): A strict JSON-parsing prompt forces the LLM to map natural language to a predefined schema of actions: open_app, type_text, hotkey, etc.
Execution (main.py): A robust execution loop that sanitizes LLM output and executes system-level operations with built-in delays for UI stability.

### 💻 Tech Stack
Component                     Technology
LLM Inference                 Groq Cloud (Llama 3.3 70B Versatile)
Language                      Python 3.10+
GUI Automation                PyAutoGUI
Speech-to-Text                Google Speech API
Text-to-Speech                Microsoft Edge TTS
