import os
import sys
import subprocess
import argparse
from google import genai
from google.genai import types

# --- Configuration ---
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- Tool Implementations ---
def Bash(command: str):
    """Executes a command in the bash shell. Use this to run python scripts."""
    print(f"\n[S] ⚡ Executing: {command}")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        display_out = output[:200] + "..." if len(output) > 200 else output
        print(f"[S] 📤 Output: {display_out.strip()}")
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"

def Edit(path: str, content: str):
    """Writes content to a file (overwrites)."""
    print(f"\n[S] ✏️ Editing file: {path}")
    try:
        with open(path, "w") as f:
            f.write(content)
        print(f"[S] ✅ File written ({len(content)} chars).")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def View(path: str):
    """Reads a file from the filesystem."""
    print(f"\n[S] 👁️ Viewing file: {path}")
    if not os.path.exists(path):
        return f"Error: File {path} not found."
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- The Agent ---

def run_mission(prompt_file=None):
    print("🤖 INITIALIZING GEMINI CODE AUTO-TEST SYSTEM...")
    
    # 1. Load Persona
    if not os.path.exists(PERSONA_FILE):
        print(f"❌ Error: Persona file {PERSONA_FILE} not found. Run the pipeline first!")
        sys.exit(1)
        
    with open(PERSONA_FILE, "r") as f:
        system_instruction = f.read()
    print(f"✅ Loaded Persona: {PERSONA_FILE}")

    # 2. Initialize Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)
    
    client = genai.Client(api_key=api_key)

    # 3. Define the Mission
    if prompt_file:
        if not os.path.exists(prompt_file):
            print(f"❌ Error: Prompt file '{prompt_file}' not found.")
            sys.exit(1)
        with open(prompt_file, 'r') as f:
            user_prompt = f.read()
        print(f"📂 Read mission from: {prompt_file}")
    else:
        # Default Hardcoded Mission
        user_prompt = (
            "MISSION: \n"
            "1. Create a python script named 'hello_math.py'.\n"
            "2. Inside, print 'Hello Gemini Code'.\n"
            "3. Also calculate the sum of 123456789 and 987654321 and print it.\n"
            "4. Execute the script using python3 and show me the output.\n"
            "IT NEEDS TO RUN AUTOMATICALLY."
        )

    print(f"\n🎯 MISSION:\n{user_prompt}\n" + "="*60)

    # 4. Start Chat with Automatic Tool Execution
    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[Bash, Edit, View],
            temperature=0.1,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=15
            )
        )
    )

    # 5. Execute
    response = chat.send_message(user_prompt)
    
    print("\n" + "="*60)
    print(f"🤖 [AGENT REPORT]:\n{response.text}")
    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent")
    parser.add_argument("prompt_file", nargs="?", help="Path to a text file containing the prompt/mission")
    args = parser.parse_args()
    
    run_mission(args.prompt_file)
