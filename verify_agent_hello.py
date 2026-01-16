import os
import sys
import time
from google import genai
from google.genai import types

# Configuration
PERSONA_PATH = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

def load_persona(path):
    """Loads the hydrated persona to simulate the actual Agent Engineer."""
    if not os.path.exists(path):
        print(f"❌ CRITICAL ERROR: Persona not found at {path}")
        print("   Run 'python hydrate_personas_v2.py' first.")
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"✅ Loaded hydrated persona: {path} ({len(content)} chars)")
        return content

def run_test():
    print(f"--- 🚀 Initializing Gemini Hello System: AGENT_ENGINEER ---")
    
    # 1. Load the Persona
    system_instruction = load_persona(PERSONA_PATH)
    
    # 2. Initialize Client
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # 3. Define the Test Prompt
    user_prompt = "Write a simple 'Hello World' script in Python. Explain how to run it."
    print(f"\n--- 🧪 Executing Hello World Test ---")
    print(f"USER >>> {user_prompt}\n")

    # 4. Generate Content (Automated - No User Input)
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            ),
            contents=user_prompt
        )

        # 5. Validate Output
        if not response.text:
            print("⚠️ Response empty.")
            sys.exit(1)

        print(f"[AGENT_ENGINEER]:\n{response.text}\n")
        print("-" * 50)

        # Validation Logic
        validation_keywords = ["print", "Hello", "World", "python"]
        if all(k in response.text for k in ["print", "Hello"]):
            print("✅ TEST PASSED: Agent successfully generated code.")
            sys.exit(0)
        else:
            print("❌ TEST FAILED: Output did not contain expected code snippets.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ API ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
