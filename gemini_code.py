# gemini_code.py
import os
import sys
from google import genai
from google.genai import types

# Configuration
MODEL_ID = "gemini-2.0-flash" 
PERSONA_DIR = "extracted_personas" 

class GeminiCodeAgent:
    def __init__(self, role_name="agent_architect"):
        self.client = genai.Client(http_options={'api_version': 'v1alpha'})
        self.role_name = role_name
        self.system_instruction = self._load_persona(role_name)
        self.chat_session = None
        
        print(f"--- 🚀 Initializing Gemini Code: {role_name.upper()} ---")

    def _load_persona(self, role_name):
        """Loads the system prompt from the extracted markdown files."""
        filename = f"{role_name}.md" if not role_name.endswith(".md") else role_name
        path = os.path.join(PERSONA_DIR, filename)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"✅ Loaded persona: {path} ({len(content)} chars)")
                return content
        except FileNotFoundError:
            print(f"❌ Error: Persona file '{path}' not found.")
            sys.exit(1)

    def start_chat(self):
        """Starts a chat session with the loaded system instruction."""
        # FIXED: chats is a top-level client member, not under models
        self.chat_session = self.client.chats.create(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7, 
            )
        )

    def send_message(self, user_input):
        """Sends a message and streams the response."""
        response = self.chat_session.send_message_stream(user_input)
        
        print(f"\n[{self.role_name.upper()}]: ", end="")
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n" + "-"*50)

def main():
    role = sys.argv[1] if len(sys.argv) > 1 else "agent_architect"
    
    agent = GeminiCodeAgent(role_name=role)
    agent.start_chat()
    
    print("Type 'exit' or 'quit' to stop. Type 'switch [agent_name]' to change personas.")
    
    while True:
        try:
            user_input = input("\n>>> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if user_input.startswith("switch "):
                new_role = user_input.split(" ")[1]
                agent = GeminiCodeAgent(role_name=new_role)
                agent.start_chat()
                continue

            agent.send_message(user_input)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
