import os
import sys
from google import genai
from google.genai import types

# Configuration
# We use the 'hydrated_personas' directory as verified in your pipeline output
PERSONA_DIR = "hydrated_personas" 
TARGET_AGENT = "agent_engineer"  # This corresponds to the "Software Engineering Assistant" found in your repo

class GeminiHelloSystem:
    def __init__(self, role_name=TARGET_AGENT):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("❌ Error: GEMINI_API_KEY not found.")
            sys.exit(1)
            
        self.client = genai.Client(api_key=self.api_key)
        self.role_name = role_name
        self.system_instruction = self._load_persona(role_name)
        self.chat_session = None
        
        print(f"--- 🚀 Initializing Gemini Hello System: {role_name.upper()} ---")

    def _load_persona(self, role_name):
        """Loads the system prompt from the HYDRATED files."""
        # We explicitly look for the .md file in the hydrated folder
        filename = f"{role_name}.md"
        path = os.path.join(PERSONA_DIR, filename)
        
        if not os.path.exists(path):
            print(f"❌ Error: Persona file '{path}' not found. Did the pipeline run?")
            # Fallback to verify if the file exists under a different name or if hydration failed
            sys.exit(1)
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"✅ Loaded hydrated persona: {path} ({len(content)} chars)")
            return content

    def run_hello_test(self):
        """Runs the Hello World test."""
        print(f"\n--- 🧪 Executing Hello World Test ---")
        
        # Configure the chat with the Agent Engineer persona
        self.chat_session = self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7, 
            )
        )
        
        user_prompt = "Write a simple 'Hello World' script in Python. Explain how to run it."
        
        print(f"USER >>> {user_prompt}\n")
        response = self.chat_session.send_message_stream(user_prompt)
        
        print(f"[{self.role_name.upper()}]: ", end="")
        full_text = ""
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                full_text += chunk.text
        print("\n" + "-"*50)
        
        if "print" in full_text and "Hello" in full_text:
            print("✅ TEST PASSED: Agent successfully generated code.")
        else:
            print("⚠️ TEST WARNING: Output verification ambiguous.")

if __name__ == "__main__":
    # Ensure we are running where the hydrated personas are
    if not os.path.exists(PERSONA_DIR):
        print(f"❌ Critical: '{PERSONA_DIR}' directory not found. Run the pipeline first!")
        sys.exit(1)
        
    system = GeminiHelloSystem()
    system.run_hello_test()
