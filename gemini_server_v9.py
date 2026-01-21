import os
import sys
import subprocess
import glob as glob_module
import http.server
import socketserver
import urllib.parse
import argparse
from google import genai
from google.genai import types
import socket
import signal
import time
import cgi
import uuid
import traceback

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description='Gemini Code Server v9 - Transparent Session')
parser.add_argument('--name', type=str, default='Agent_v9', help='Agent name')
parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
parser.add_argument('--force', action='store_true', help='Force takeover of the port')
args = parser.parse_args()

AGENT_NAME = args.name
SERVER_PORT = args.port
FORCE_TAKEOVER = args.force

# --- Configuration ---
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- Global State ---
history_log = []
chat_session = None
current_model_id = None

# --- 1. Runtime Tool Definitions ---

def Bash(command: str):
    """Executes a command in the bash shell. Output is logged for the user."""
    print(f"\n[SERVER] ⚡ Executing Bash: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        output = output if output else "(No output)"
        # FIX: Explicitly log result so user can see it in UI
        history_log.append(("TOOL", f"CMD: {command}\n{output}"))
        return output
    except Exception as e:
        msg = f"Error executing command: {str(e)}"
        history_log.append(("TOOL", msg))
        return msg

def View(path: str):
    """Reads and displays the contents of a file."""
    print(f"\n[SERVER] 👁️ Viewing file: {path}")
    if not os.path.exists(path):
        return f"Error: File {path} not found."
    try:
        with open(path, "r") as f:
            content = f.read()
            history_log.append(("TOOL", f"VIEW: {path}\n{content}"))
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def Glob(pattern: str):
    """Lists files matching a pattern."""
    try:
        files = glob_module.glob(pattern, recursive=True)
        res = "\n".join(files) if files else "No files found."
        history_log.append(("TOOL", f"GLOB: {pattern}\n{res}"))
        return res
    except Exception as e:
        return f"Error: {str(e)}"

def Grep(pattern: str, path: str):
    """Searches files for a pattern."""
    try:
        cmd = ["grep", "-r", pattern, path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        res = result.stdout if result.stdout else "No matches found."
        history_log.append(("TOOL", f"GREP: {pattern} in {path}\n{res}"))
        return res
    except Exception as e:
        return f"Error: {str(e)}"

# --- 2. Agent Initialization ---

if not os.path.exists(PERSONA_FILE):
    SYSTEM_INSTRUCTION = "You are an expert Software Engineer agent. You can execute bash commands, edit files, and view files."
else:
    with open(PERSONA_FILE, "r") as f:
        SYSTEM_INSTRUCTION = f.read()

SYSTEM_INSTRUCTION += f"\nSYSTEM CONTEXT: You are {AGENT_NAME}. Output of your tools is displayed to the user automatically."

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# --- 3. Server Implementation ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Code Console v9</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/marked/marked.min.css">
    <style>
        body { font-family: 'Segoe UI', monospace; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box;}
        #chat-history { flex: 1; overflow-y: auto; background: #252526; border: 1px solid #3c3c3c; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .msg { margin-bottom: 15px; white-space: pre-wrap; line-height: 1.4; padding: 10px; border-radius: 4px; }
        .user-msg { color: #4ec9b0; background: #2d2d2d; border-left: 4px solid #4ec9b0; }
        .agent-msg { color: #ce9178; background: #2d2d2d; border-left: 4px solid #ce9178; }
        .tool-msg { color: #858585; background: #1a1a1a; border-left: 4px solid #666; font-size: 0.9em; font-family: 'Consolas', monospace; }
        form { display: flex; gap: 10px; }
        textarea { flex: 1; background: #3c3c3c; color: #fff; border: 1px solid #007acc; padding: 10px; border-radius: 4px; height: 60px;}
        button { background: #0e639c; color: white; border: none; padding: 0 20px; cursor: pointer; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🤖 Gemini Code Console (Persistent v9)</h1>
    <div id="chat-history">{{CHAT_HISTORY}}</div>
    <form method="POST" action="/" enctype="multipart/form-data">
        <select name="model_choice">
          <option value="gemini-2.0-flash">gemini-2.0-flash</option>
          <option value="gemini-2.0-pro">gemini-2.0-pro</option>
        </select>
        <textarea name="prompt" placeholder="Execute command..." autofocus></textarea>
        <button type="submit">Run</button>
    </form>
    <script>
        const history = document.getElementById('chat-history');
        history.scrollTop = history.scrollHeight;
    </script>
</body>
</html>
"""

class GeminiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            history_html = ""
            for role, text in history_log:
                if role == "USER": css = "user-msg"
                elif role == "GEMINI": css = "agent-msg"
                else: css = "tool-msg"
                safe_text = (text or "").replace("<", "&lt;").replace(">", "&gt;")
                history_html += f'<div class="msg {css}">{safe_text}</div>'
            self.wfile.write(HTML_TEMPLATE.replace("{{CHAT_HISTORY}}", history_html).encode())
        else: super().do_GET()

    def do_POST(self):
        global chat_session, current_model_id
        if self.path == "/":
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
            model_choice = form.getvalue('model_choice')
            user_prompt = form.getvalue('prompt')

            if user_prompt:
                history_log.append(("USER", user_prompt))
                try:
                    # Persistence Check
                    if chat_session is None or model_choice != current_model_id:
                        current_model_id = model_choice
                        chat_session = client.chats.create(
                            model=model_choice,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_INSTRUCTION,
                                tools=[Bash, View, Glob, Grep],
                                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                            )
                        )
                    response = chat_session.send_message(user_prompt)
                    output_text = response.text if response.text else "(Command Executed)"
                    history_log.append(("GEMINI", output_text))
                except Exception as e:
                    history_log.append(("GEMINI", f"❌ Error: {str(e)}"))

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

if __name__ == "__main__":
    # Same takeover logic from v8
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', SERVER_PORT))
    except OSError:
        if FORCE_TAKEOVER:
            result = subprocess.run(f"lsof -t -i:{SERVER_PORT}", shell=True, capture_output=True, text=True)
            if result.stdout:
                os.kill(int(result.stdout.strip()), signal.SIGTERM)
                time.sleep(1)
    finally: sock.close()

    print(f"📡 Serving v9 on Port {SERVER_PORT}...")
    with socketserver.ThreadingTCPServer(("", SERVER_PORT), GeminiHandler) as httpd:
        httpd.serve_forever()
