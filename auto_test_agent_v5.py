import os
import sys
import subprocess
import argparse
from google import genai
from google.genai import types

# --- Configuration ---
DEFAULT_PERSONA = "hydrated_personas/agent_engineer.md"
DEFAULT_MODEL = "gemini-2.0-flash"

# --- Tool Implementations (v5 Upgrades) ---

def Bash(command: str):
    """Executes a command. Returns stdout, stderr, and EXIT CODE. Use this for standard ops."""
    print(f"\n[S] ⚡ Bash: {command}")
    try:
        # v5: Explicit executable and shell=True for pipes
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120,
            executable="/bin/bash" 
        )
        
        # v5: Clear reporting of exit codes to prevent "silent failures"
        output_str = f"EXIT_CODE: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        
        # Truncate for display only
        display_out = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
        print(f"[S] 📤 Output ({result.returncode}): {display_out.strip()}")
        
        return output_str
    except Exception as e:
        return f"EXECUTION_ERROR: {str(e)}"

def SudoBash(command: str):
    """Tries to execute with 'sudo -n' (non-interactive). Use ONLY for killing stubborn PIDs or system ports."""
    print(f"\n[S] 🛡️ SudoBash: {command}")
    return Bash(f"sudo -n {command}")

def Edit(path: str, content: str):
    """Writes content to a file (overwrites). Handles home directory expansion."""
    expanded_path = os.path.expanduser(path)
    print(f"\n[S] ✏️ Editing file: {expanded_path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(expanded_path)), exist_ok=True)
        with open(expanded_path, "w") as f:
            f.write(content)
        print(f"[S] ✅ File written ({len(content)} chars).")
        return f"Successfully wrote to {expanded_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def View(path: str):
    """Reads a file from the filesystem."""
    expanded_path = os.path.expanduser(path)
    print(f"\n[S] 👁️ Viewing file: {expanded_path}")
    if not os.path.exists(expanded_path):
        return f"Error: File {expanded_path} not found."
    try:
        with open(expanded_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- The Agent ---

def run_mission(prompt_file=None, model_id=DEFAULT_MODEL, persona_path=DEFAULT_PERSONA):
    print("🤖 INITIALIZING GEMINI CODE AUTO-TEST SYSTEM (v5 - ROOT AWARE)...")
    
    # 1. Environment Check
    user = os.getenv("USER", "unknown")
    print(f"👤 Current User: {user}")
    if user != "root":
        print("⚠️  WARNING: You are NOT root. Permission errors may occur.")

    # 2. Load Persona with v5 Override
    system_instruction = ""
    if os.path.exists(persona_path):
        with open(persona_path, "r") as f:
            raw_persona = f.read()
        print(f"✅ Loaded Persona: {persona_path}")
        
        system_instruction = (
            f"{raw_persona}\n\n"
            "SYSTEM OVERRIDE v5 (ROBUSTNESS):\n"
            "1. You are in AUTONOMOUS MODE. Do not ask for help.\n"
            "2. ALWAYS check the 'EXIT_CODE' in Bash results. 0 = Success. Anything else = Failure.\n"
            "3. If a process refuses to die, try 'SudoBash'.\n"
            "4. When finding PIDs, use 'lsof -t -i:8080' or 'fuser 8080/tcp' if possible, it is more accurate than grep.\n"
            "5. Your goal is to kill the zombie on port 8080 and start gemini_server_v7.py.\n"
        )
    else:
        system_instruction = "You are an expert autonomous engineer. Fix the broken server deployment."

    # 3. Initialize Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)
    
    client = genai.Client(api_key=api_key)

    # 4. Define the Mission
    if prompt_file:
        with open(prompt_file, 'r') as f:
            user_prompt = f.read()
    else:
        user_prompt = "Identify the process on port 8080. Kill it. Start gemini_server_v7.py on 8080. Verify it returns HTML, not JSON."

    print(f"\n🎯 MISSION:\n{user_prompt}\n" + "="*60)

    # 5. Start Chat
    chat = client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[Bash, SudoBash, Edit, View], # Added SudoBash
            temperature=0.1, 
        )
    )

    # 6. Execute
    final_prompt = f"{user_prompt}\n\n(REMINDER: Check EXIT_CODES. Verify the kill before starting the new server.)"
    
    try:
        response = chat.send_message(final_prompt)
        print("\n" + "="*60)
        # Handle cases where the model calls tools but returns no text
        if response.text:
            print(f"🤖 [AGENT REPORT]:\n{response.text}")
        else:
            print(f"🤖 [AGENT COMPLETED MISSION] (No text summary returned)")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent v5")
    parser.add_argument("prompt_file", nargs="?", help="Path to mission file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID")
    parser.add_argument("--persona", default=DEFAULT_PERSONA, help="Persona path")
    args = parser.parse_args()
    
    run_mission(args.prompt_file, args.model, args.persona)
