import os
import sys
import subprocess
from google import genai
from google.genai import types

# --- Configuration ---
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- Tool Implementations (The "Runtime") ---
# These function names match the 'master_tool_definitions.json' extract

def Bash(command: str):
    """Executes a command in the bash shell. Use this to run python scripts."""
    print(f"\n[S] ⚡ Executing: {command}")
    try:
        # Safety: Timeout to prevent hangs
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        # Truncate output if massive
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

def run_mission():
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
    user_prompt = (
        "MISSION: \n"
        "1. Create a python script named 'hello_math.py'.\n"
        "2. Inside, print 'Hello Gemini Code'.\n"
        "3. Also calculate the sum of 123456789 and 987654321 and print it.\n"
        "4. Execute the script using python3 and show me the output.\n"
        "IT NEEDS TO RUN AUTOMATICALLY."
    )

    print(f"\n🎯 MISSION: {user_prompt}\n" + "="*60)

    # 4. Start Chat with Automatic Tool Execution
    # We pass the python functions directly; the SDK handles serialization/execution
    chat = client.chats.create(
        model=MODEL_ID,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[Bash, Edit, View], # Register our runtime tools
            temperature=0.1, # Low temp for precise coding
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=10 # Prevent infinite loops
            )
        )
    )

    # 5. Execute
    response = chat.send_message(user_prompt)
    
    print("\n" + "="*60)
    print(f"🤖 [AGENT REPORT]:\n{response.text}")
    print("="*60)

    # 6. Verification
    print("\n🔎 VERIFYING OUTPUT...")
    if os.path.exists("hello_math.py"):
        print("✅ 'hello_math.py' exists.")
        output = subprocess.getoutput("python3 hello_math.py")
        if "1111111110" in output:
             print("✅ Math verified (1111111110 found).")
             print("✨ TEST PASSED: Gemini Code is Operational.")
        else:
             print(f"⚠️ Math verification failed. Output:\n{output}")
    else:
        print("❌ 'hello_math.py' was NOT created.")

if __name__ == "__main__":
    run_mission()
