import os
from google import genai
from google.genai import types

# Load the hydrated Engineer persona
with open("hydrated_personas/agent_engineer.md", "r") as f:
    SYSTEM_PROMPT = f.read()

# Load the tools we think we have (combine browser and reconstructed core)
import json
with open("core_tools_reconstructed.json", "r") as f:
    core_tools = json.load(f)
with open("gemini_browser_tools.json", "r") as f:
    browser_tools = json.load(f)

all_tools_definitions = core_tools # + browser_tools (Keep it simple for now)

print(f"--- 🧪 Dry Run: Agent Engineer ---")
print(f"System Prompt Length: {len(SYSTEM_PROMPT)} chars")
print(f"Loaded Tools: {[t['function']['name'] for t in all_tools_definitions]}")

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Create the chat
chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=all_tools_definitions,
        temperature=0.0 # Strict for testing
    )
)

# User Simulation: A typical coding task
user_msg = "Please check the file 'main.py' and change the print statement to say 'Hello World'."
print(f"\nUser: {user_msg}")

response = chat.send_message(user_msg)

print("\n--- 🤖 Model Response ---")
# Check if it tried to call a tool
for part in response.candidates[0].content.parts:
    if part.function_call:
        print(f"✅ TOOL CALL DETECTED: {part.function_call.name}")
        print(f"   Args: {part.function_call.args}")
        
        # Validation Logic
        if part.function_call.name == "Edit":
            args = part.function_call.args
            if "content" in args and "old_string" not in args:
                print("⚠️ WARNING: Model used full-file overwrite ('content'). Check if 'str_replace' is preferred.")
    elif part.text:
        print(f"Text: {part.text}")
