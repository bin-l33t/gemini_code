import os
import sys
import subprocess
import argparse
import time
from google import genai
from google.genai import types

# --- Configuration ---
DEFAULT_PERSONA = "hydrated_personas/agent_engineer.md"
DEFAULT_MODEL = "gemini-2.0-flash"

# --- Tool Implementations (v6 Upgrades) ---

def Bash(command: str):
    """Executes a command. Returns stdout, stderr, and EXIT CODE. Use this for standard ops."""
    print(f"\n[S] ⚡ Bash: {command}")
    try:
        # v6: Explicit executable
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=120,
            executable="/bin/bash" 
        )
        
        # v6: BETTER LOGGING - Print Stderr to console if it exists
        display_out = result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout
        display_err = result.stderr[:300] + "..." if len(result.stderr) > 300 else result.stderr
        
        print(f"[S] 📤 STDOUT ({result.returncode}): {display_out.strip()}")
        if display_err.strip():
            print(f"[S] ⚠️ STDERR: {display_err.strip()}")
        
        output_str = f"EXIT_CODE: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return output_str
    except Exception as e:
        return f"EXECUTION_ERROR: {str(e)}"

def InspectPort(port: int):
    """v6 NEW: Returns detailed info (PID, User, Command) for the process on a port."""
    print(f"\n[S] 🔍 Inspecting Port: {port}")
    try:
        # Try lsof first (more reliable for ports)
        cmd = f"lsof -i :{port} -t"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        pid = result.stdout.strip()
        
        if not pid:
            # Try ss as fallback
            cmd_ss = f"ss -lptn 'sport = :{port}' | grep -o 'pid=[0-9]*' | cut -d= -f2"
            result_ss = subprocess.run(cmd_ss, shell=True, capture_output=True, text=True)
            pid = result_ss.stdout.strip()

        if not pid:
            print("[S] 🚫 Port is free (no PID found).")
            return "PORT_STATUS: FREE"
        
        # Get process details using ps
        print(f"[S] 🕵️ Found PID {pid}. Fetching details...")
        ps_cmd = f"ps -fp {pid}"
        ps_result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
        
        return f"PORT_STATUS: OCCUPIED\nPID: {pid}\nDETAILS:\n{ps_result.stdout}"
    except Exception as e:
        return f"INSPECTION_ERROR: {str(e)}"

def KillProcess(pid: int):
    """v6 NEW: Smart kill. Tries SIGTERM, waits, checks, then tries Sudo if needed."""
    print(f"\n[S] 💀 Attempting to kill PID: {pid}")
    
    # 1. Try standard kill
    subprocess.run(f"kill {pid}", shell=True)
    time.sleep(1) # Give it a moment to die
    
    # 2. Check if still alive
    check = subprocess.run(f"ps -p {pid}", shell=True, capture_output=True)
    if check.returncode != 0:
        print("[S] ☠️ Process successfully killed.")
        return "STATUS: KILLED (Standard)"
    
    # 3. Try Sudo Kill (Non-interactive)
    print("[S] 🛡️ Standard kill failed. Trying sudo -n kill -9...")
    sudo_res = subprocess.run(f"sudo -n kill -9 {pid}", shell=True, capture_output=True, text=True)
    
    if sudo_res.returncode == 0:
        print("[S] ☠️ Process killed with SUDO.")
        return "STATUS: KILLED (Sudo Force)"
    else:
        print(f"[S] ❌ Sudo failed. Output: {sudo_res.stderr}")
        return f"STATUS: FAILED_TO_KILL. Stderr: {sudo_res.stderr}"

def Edit(path: str, content: str):
    """Writes content to a file (overwrites)."""
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
    print("🤖 INITIALIZING GEMINI CODE AUTO-TEST SYSTEM (v6 - DIAGNOSTIC MODE)...")
    
    # 1. Environment Check
    user = os.getenv("USER", "unknown")
    print(f"👤 Current User: {user}")
    
    # 2. Load Persona
    system_instruction = ""
    if os.path.exists(persona_path):
        with open(persona_path, "r") as f:
            raw_persona = f.read()
        print(f"✅ Loaded Persona: {persona_path}")
        
        system_instruction = (
            f"{raw_persona}\n\n"
            "SYSTEM OVERRIDE v6 (DIAGNOSTICS):\n"
            "1. USE 'InspectPort(8080)' FIRST to see EXACTLY what command is running (e.g., 'python3 gemini_server_v7.py').\n"
            "2. USE 'KillProcess(pid)' to handle killing. It will verify death for you.\n"
            "3. If the mission fails verification but 'InspectPort' confirms 'gemini_server_v7.py' is running, suspect the server code itself is wrong (returns JSON instead of HTML).\n"
        )
    else:
        system_instruction = "You are an expert autonomous engineer."

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
        user_prompt = "Identify the process on port 8080. Kill it. Start gemini_server_v7.py on 8080. Verify output."

    print(f"\n🎯 MISSION:\n{user_prompt}\n" + "="*60)

    # 5. Start Chat
    chat = client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[Bash, InspectPort, KillProcess, Edit, View], 
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent v6")
    parser.add_argument("prompt_file", nargs="?", help="Path to mission file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID")
    parser.add_argument("--persona", default=DEFAULT_PERSONA, help="Persona path")
    args = parser.parse_args()
    
    run_mission(args.prompt_file, args.model, args.persona)
