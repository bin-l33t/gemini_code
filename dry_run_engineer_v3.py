import os
from google import genai
from google.genai import types
import bridge_tools # Import the script above

# 1. Setup Client
client = genai.Client(http_options={'api_version': 'v1alpha'})

# 2. Load Tools using the Bridge
gemini_tools = bridge_tools.load_all_tools()
print(f"✅ Loaded {len(gemini_tools.function_declarations)} tools into Gemini format.")

# 3. Load Persona
with open("hydrated_personas/agent_engineer.md", "r") as f:
    system_instruction = f.read()

# 4. Configure Chat
config = types.GenerateContentConfig(
    tools=[gemini_tools], # Note: Must be a list of Tool objects
    system_instruction=system_instruction,
    temperature=0.7
)

# 5. Run Test
print("--- 🧪 Starting Chat Session ---")
chat = client.chats.create(model="gemini-2.0-flash", config=config)
response = chat.send_message("Please check the current directory for any python files.")

print(f"User: Please check the current directory for any python files.")
print(f"Model Response: {response.text}")

# Check for function calls
if response.function_calls:
    for fc in response.function_calls:
        print(f"🛠️  TOOL TRIGGERED: {fc.name}({fc.args})")
