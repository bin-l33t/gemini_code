
import os
import sys
from google import genai
from google.genai import types

def run_mission(prompt_input=None, model_id="gemini-2.0-flash", persona_path="hydrated_personas/agent_engineer.md", tools=None):
    print("🤖 INITIALIZING GEMINI CODE AUTO-TEST SYSTEM (Swarm Architecture)...")

    # 1. Environment Check
    user = os.getenv("USER", "unknown")
    print(f"👤 Current User: {user}")

    # 2. Load Persona
    system_instruction = ""
    if os.path.exists(persona_path):
        with open(persona_path, "r") as f:
            raw_persona = f.read()
        print(f"✅ Loaded Persona: {persona_path}")

        system_instruction = raw_persona
    else:
        system_instruction = "You are an expert autonomous engineer. Your goal is to complete the given mission using the available tools."
        print("⚠️ Persona file not found. Using fallback persona.")

    # 3. Initialize Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # 4. Define the Mission (v7 Logic)
    user_prompt = "No mission specified."

    if prompt_input:
        is_file = False
        try:
            # Check if it's a file path.
            # If the name is too long (OSError 36), prompt_input is clearly raw text.
            if os.path.exists(prompt_input):
                is_file = True
        except OSError:
            is_file = False

        if is_file:
            try:
                with open(prompt_input, 'r') as f:
                    user_prompt = f.read()
                print(f"📂 Loaded Mission from file: {prompt_input}")
            except Exception as e:
                # Fallback if file open fails
                print(f"⚠️ Could not open file '{prompt_input}' ({e}). Treating as text.")
                user_prompt = prompt_input
        else:
            print("🗣️ Received Mission as direct text input.")
            user_prompt = prompt_input

    print(f"\n🎯 MISSION:\n{user_prompt}\n" + "="*60)

    # 5. Start Chat
    chat = client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=0.1,
        )
    )

    # 6. Execute
    final_prompt = f"{user_prompt}\n\n(HINT: Use InspectPort to verify the process command line matches the target file.)"

    try:
        response = chat.send_message(final_prompt)
        print("\n" + "="*60)
        if response.text:
            print(f"🤖 [AGENT REPORT]:\n{response.text}")
        else:
            print(f"🤖 [AGENT COMPLETED MISSION] (No text summary returned)")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")

