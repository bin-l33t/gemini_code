import os
import sys
import subprocess
import json
from google import genai
from google.genai import types

# Configuration
MODEL_ID = "gemini-2.0-flash"
PERSONA_PATH = "hydrated_personas/agent_engineer.md"

# --- 1. Define the Bash Tool ---
def execute_bash(command):
    """Executes a bash command and returns stdout/stderr."""
    print(f"\n[S] ⚡ Executing: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        output = result.stdout + result.stderr
        # Truncate if massive
        if len(output) > 2000:
            return output[:2000] + "... [truncated]"
        return output
    except Exception as e:
        return f"Execution failed: {str(e)}"

# Schema for Gemini
bash_tool_schema = {
    "name": "Bash",
    "description": "Execute a bash command on the local system. Use this to write files (echo/printf) or run scripts.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute."
            }
        },
        "required": ["command"]
    }
}

# --- 2. The Agent Logic ---
class AutoAgent:
    def __init__(self):
        self.client = genai.Client(http_options={'api_version': 'v1alpha'})
        self.system_instruction = self._load_persona()
        self.history = []

    def _load_persona(self):
        if not os.path.exists(PERSONA_PATH):
            # Fallback if hydrated path missing
            return "You are an expert Software Engineer. You write and execute code to solve problems."
        with open(PERSONA_PATH, "r") as f:
            print(f"✅ Loaded Persona: {PERSONA_PATH}")
            return f.read()

    def run_mission(self, prompt):
        print(f"\n🤖 AGENT MISSION: {prompt}")
        
        # Start chat with tools
        chat = self.client.chats.create(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=[types.Tool(function_declarations=[bash_tool_schema])],
                temperature=0.1 # Low temp for precise coding
            )
        )
        
        # Send initial message
        response = chat.send_message(prompt)
        self._handle_response_loop(chat, response)

    def _handle_response_loop(self, chat, response):
        """Loop to handle tool calls until text is generated."""
        turn_limit = 10
        current_turn = 0
        
        while current_turn < turn_limit:
            current_turn += 1
            part = response.candidates[0].content.parts[0]

            # Case A: Tool Call (The Agent wants to do something)
            if part.function_call:
                fname = part.function_call.name
                fargs = part.function_call.args
                
                if fname == "Bash":
                    cmd = fargs.get("command")
                    tool_output = execute_bash(cmd)
                    
                    # Send output back to Agent
                    print(f"[S] 📤 Sending Tool Output ({len(tool_output)} chars)...")
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name="Bash",
                            response={"result": tool_output}
                        )
                    )
                else:
                    print(f"❌ Unknown tool: {fname}")
                    break
            
            # Case B: Text Response (The Agent is talking to us)
            elif part.text:
                print(f"\n[AGENT]: {part.text}")
                if "1111111110" in part.text or "execution complete" in part.text.lower():
                    print("\n✅ MISSION SUCCESS: Math verified in output.")
                    break
                # If it just talked but didn't run the code yet, we might need to nudge, 
                # but usually it chains the tool call before final text.
                break
                
            else:
                print("⚠️ Unexpected response format.")
                break

# --- 3. Execution ---
if __name__ == "__main__":
    agent = AutoAgent()
    
    # The Request: Write code, Run code, Verify Math
    mission = (
        "1. Create a python script named 'hello_math.py'. "
        "2. Inside, print 'Hello Gemini Code'. "
        "3. Also calculate the sum of 123456789 and 987654321 and print it. "
        "4. Execute the script using python3 and show me the output."
    )
    
    agent.run_mission(mission)
