import os
import subprocess
import time

def Bash(command: str):
    """Executes a command. Returns stdout, stderr, and EXIT CODE. Use this for standard ops."""
    print(f"\n[S] ⚡ Bash: {command}")
    try:
        # Explicit executable for consistency
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            executable="/bin/bash"
        )

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
    """Returns detailed info (PID, User, Command) for the process on a port."""
    print(f"\n[S] 🔍 Inspecting Port: {port}")
    try:
        # Try lsof first
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

        # Get process details
        print(f"[S] 🕵️ Found PID {pid}. Fetching details...")
        ps_cmd = f"ps -fp {pid}"
        ps_result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)

        return f"PORT_STATUS: OCCUPIED\nPID: {pid}\nDETAILS:\n{ps_result.stdout}"
    except Exception as e:
        return f"INSPECTION_ERROR: {str(e)}"

def KillProcess(pid: int):
    """Smart kill. Tries SIGTERM, waits, checks, then tries Sudo if needed."""
    print(f"\n[S] 💀 Attempting to kill PID: {pid}")

    # 1. Try standard kill
    subprocess.run(f"kill {pid}", shell=True)
    time.sleep(1)

    # 2. Check if still alive
    check = subprocess.run(f"ps -p {pid}", shell=True, capture_output=True)
    if check.returncode != 0:
        print("[S] ☠️ Process successfully killed.")
        return "STATUS: KILLED (Standard)"

    # 3. Try Sudo Kill
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

def SmartRead(path: str, lines: int = 500, from_bottom: bool = False):
    """Reads a file from the filesystem, optionally from the bottom."""
    expanded_path = os.path.expanduser(path)
    print(f"\n[S] 👁️ Smart Reading file: {expanded_path} (lines={lines}, from_bottom={from_bottom})")
    if not os.path.exists(expanded_path):
        return f"Error: File {expanded_path} not found."
    try:
        with open(expanded_path, "r") as f:
            all_lines = f.readlines()
        
        if from_bottom:
            selected_lines = all_lines[-lines:]
        else:
            selected_lines = all_lines[:lines]
        
        return "".join(selected_lines)
    except Exception as e:
        return f"Error reading file: {str(e)}"

def SpawnSubAgent(mission: str, blocking: bool):
    """Spawns a sub-agent with the given mission."""
    print(f"\n[S] 👶 Spawning Sub-Agent: mission='{mission}', blocking={blocking}")
    try:
        if blocking:
            result = subprocess.run(
                [sys.executable, __file__, mission],
                capture_output=True,
                text=True,
                timeout=300 # Increased timeout for blocking calls
            )
            print(f"[S] 👶 Sub-Agent completed (blocking).")
            display_out = result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout
            display_err = result.stderr[:300] + "..." if len(result.stderr) > 300 else result.stderr

            print(f"[S] 📤 Sub-Agent STDOUT ({result.returncode}): {display_out.strip()}")
            if display_err.strip():
                print(f"[S] ⚠️ Sub-Agent STDERR: {display_err.strip()}")
            return f"Sub-Agent completed. STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        else:
            subprocess.Popen(
                [sys.executable, __file__, mission],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[S] 👶 Sub-Agent spawned (non-blocking).")
            return "Sub-Agent spawned (non-blocking)."
    except Exception as e:
        return f"Error spawning sub-agent: {str(e)}"


def browser_evaluate(action, coords):
    print(f"[MOCK TOOL] Would have executed action: {action} on coordinates: {coords}")

def click(action, coords):
    print(f"[MOCK TOOL] Would have executed action: {action} on coordinates: {coords}")

def type(action, coords):
    print(f"[MOCK TOOL] Would have executed action: {action} on coordinates: {coords}")

def scroll(action, coords):
    print(f"[MOCK TOOL] Would have executed action: {action} on coordinates: {coords}")

def screenshot(action, coords):
    print(f"[MOCK TOOL] Would have executed action: {action} on coordinates: {coords}")
