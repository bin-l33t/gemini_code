import os
import sys
import subprocess
import argparse
from google import genai
from google.genai import types

# --- Configuration ---
DEFAULT_PERSONA = "hydrated_personas/agent_engineer.md"
DEFAULT_MODEL = "gemini-2.0-flash"

# --- Tool Implementations (Merged v2 UX + v3 Robustness) ---

def Bash(command: str):
    """Executes a command in the bash shell. Use this to run python scripts."""
    print(f"\n[S] ⚡ Executing: {command}")
    try:
        # v2 style execution (simpler for agents) with v3-like shell safety
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120, # Increased timeout for installs/long scripts
            executable="/bin/bash" # Explicitly use bash like v3
        )
        output = result.stdout + result.stderr
        display_out = output[:200] + "..." if len(output) > 200 else output
        print(f"[S] 📤 Output: {display_out.strip()}")
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"

def Edit(path: str, content: str):
    """Writes content to a file (overwrites). Handles home directory expansion."""
    # v3 Robustness: Expand user paths (~)
    expanded_path = os.path.expanduser(path)
    
    # v2 UX: Console feedback
    print(f"\n[S] ✏️ Editing file: {expanded_path}")
    
    try:
        # Ensure directory exists (Robustness improvement)
        os.makedirs(os.path.dirname(os.path.abspath(expanded_path)), exist_ok=True)
        
        with open(expanded_path, "w") as f:
            f.write(content)
        
        print(f"[S] ✅ File written ({len(content)} chars).")
        return f"Successfully wrote to {expanded_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def View(path: str):
    """Reads a file from the filesystem. Handles home directory expansion."""
    # v3 Robustness: Expand user paths (~)
    expanded_path = os.path.expanduser(path)
    
    # v2 UX: Console feedback
    print(f"\n[S] 👁️ Viewing file: {expanded_path}")
    
    if not os.path.exists(expanded_path):
        return f"Error: File {expanded_path} not found."
    
    try:
        with open(expanded_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- The Agent (Preserved from v2) ---

def run_mission(prompt_file=None, model_id=DEFAULT_MODEL, persona_path=DEFAULT_PERSONA):
    print("🤖 INITIALIZING GEMINI CODE AUTO-TEST SYSTEM (v4)...")
    
    # 1. Load Persona with AUTO-OVERRIDE
    system_instruction = ""
    if os.path.exists(persona_path):
        with open(persona_path, "r") as f:
            raw_persona = f.read()
        print(f"✅ Loaded Persona: {persona_path}")
        
        # Override to ensure autonomy
        system_instruction = (
            f"{raw_persona}\n\n"
            "IMPORTANT SYSTEM OVERRIDE:\n"
            "You are currently running in fully AUTONOMOUS mode via a script.\n"
            "1. DO NOT ask the user for input, code snippets, or decisions.\n"
            "2. DO NOT stop to teach or explain concepts.\n"
            "3. IMPLEMENT all code logic yourself immediately.\n"
            "4. Your goal is to complete the mission using tools as fast as possible.\n"
        )
    else:
        print(f"⚠️ Warning: Persona {persona_path} not found. Using default generic engineer.")
        system_instruction = (
            "You are an expert autonomous software engineer. "
            "You have access to Bash, Edit, and View tools. "
            "Receive a mission, plan the steps, and execute them automatically. "
            "Write the code yourself. Do not ask the user for help."
        )

    # 2. Initialize Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)
    
    # Correct v2 SDK usage
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
        user_prompt = "Calculate the md5 sum of the file 'auto_test_agent_v4.py' and print it."

    print(f"\n🎯 MISSION:\n{user_prompt}\n" + "="*60)

    # 4. Start Chat
    chat = client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[Bash, Edit, View],
            temperature=0.1, 
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=20 
            )
        )
    )

    # 5. Execute
    final_prompt = f"{user_prompt}\n\n(REMINDER: Execute all steps automatically. Write all code yourself.)"
    
    try:
        response = chat.send_message(final_prompt)
        print("\n" + "="*60)
        print(f"🤖 [AGENT REPORT]:\n{response.text}")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent v4")
    parser.add_argument("prompt_file", nargs="?", help="Path to a text file containing the prompt/mission")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini Model ID (default: gemini-2.0-flash)")
    parser.add_argument("--persona", default=DEFAULT_PERSONA, help="Path to persona file")
    
    args = parser.parse_args()
    
    run_mission(args.prompt_file, args.model, args.persona)
