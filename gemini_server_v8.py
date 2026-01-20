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

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description='Gemini Code Server with Agent Identity')
parser.add_argument('--name', type=str, default='Agent', help='Agent name')
parser.add_argument('--port', type=int, default=8888, help='Port to run the server on')
parser.add_argument('--force', action='store_true', help='Force takeover of the port')
args = parser.parse_args()

AGENT_NAME = args.name
SERVER_PORT = args.port
OTHER_PORT = 8081 if SERVER_PORT == 8080 else 8080
FORCE_TAKEOVER = args.force

# --- Configuration ---
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- 1. Runtime Tool Definitions ---

def Bash(command: str):
    """Executes a command in the bash shell. Use this to run system commands or scripts."""
    print(f"\n[SERVER] ⚡ Executing Bash: {command}")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        display_out = output[:200] + "..." if len(output) > 200 else output
        print(f"[SERVER] 📤 Output: {display_out.strip()}")
        return output if output else "(No output)"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def Edit(path: str, content: str):
    """Writes content to a file (overwrites)."""
    print(f"\n[SERVER] ✏️ Editing file: {path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def View(path: str):
    """Reads and displays the contents of a file."""
    print(f"\n[SERVER] 👁️ Viewing file: {path}")
    if not os.path.exists(path):
        return f"Error: File {path} not found."
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def Glob(pattern: str):
    """Lists files matching a pattern (e.g., *.py)."""
    try:
        files = glob_module.glob(pattern, recursive=True)
        return "\n".join(files) if files else "No files found."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def Grep(pattern: str, path: str):
    """Searches files for a pattern using grep."""
    try:
        cmd = ["grep", "-r", pattern, path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout if result.stdout else "No matches found."
    except Exception as e:
        return f"Error executing grep: {str(e)}"

# --- 2. Agent Initialization ---

print("🤖 INITIALIZING GEMINI CODE SERVER (Single Page Mode)...")

if not os.path.exists(PERSONA_FILE):
    # Fallback if specific persona missing
    print(f"⚠️  Warning: {PERSONA_FILE} not found. Using default engineer prompt.")
    SYSTEM_INSTRUCTION = "You are an expert Software Engineer agent. You can execute bash commands, edit files, and view files."
else:
    with open(PERSONA_FILE, "r") as f:
        SYSTEM_INSTRUCTION = f.read()
    print(f"✅ Loaded Persona: {PERSONA_FILE}")

# Append dynamic footer to system instruction
SYSTEM_INSTRUCTION += f"\nSYSTEM CONTEXT: You are {AGENT_NAME}. You are running on port {SERVER_PORT}. You have permission to manage the process on port {OTHER_PORT} if needed."

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

chat_session = client.chats.create(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[Bash, Edit, View, Glob, Grep],
        temperature=0.1,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=False,
            maximum_remote_calls=15
        )
    )
)

# --- 3. Server Implementation ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Code Console</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/marked/marked.min.css">
    <style>
        body { font-family: 'Segoe UI', monospace; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box;}
        h1 { color: #fff; margin-top: 0; font-size: 1.2rem; border-bottom: 1px solid #333; padding-bottom: 10px; }
        #chat-history { flex: 1; overflow-y: auto; background: #252526; border: 1px solid #3c3c3c; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .msg { margin-bottom: 15px; white-space: pre-wrap; line-height: 1.4; }
        .user-msg { color: #4ec9b0; font-weight: bold; border-left: 3px solid #4ec9b0; padding-left: 10px; }
        .agent-msg { color: #ce9178; border-left: 3px solid #ce9178; padding-left: 10px; }
        .agent-msg pre { background-color: #333; padding: 5px; overflow-x: auto; }
        form { display: flex; gap: 10px; height: 50px; }
        textarea { flex: 1; background: #3c3c3c; color: #fff; border: 1px solid #007acc; border-radius: 4px; padding: 10px; resize: none; font-family: inherit; }
        textarea:focus { outline: none; background: #444; }
        button { background: #0e639c; color: white; border: none; padding: 0 20px; cursor: pointer; border-radius: 4px; font-weight: bold; }
        button:hover { background: #1177bb; }
        #thinking { color: #f0ad4e; margin-top: 5px; display: none; }
    </style>
</head>
<body>
    <h1>🤖 Gemini Code Console</h1>
    <div id="chat-history">
        {{CHAT_HISTORY}}
    </div>
    <form method="POST" action="/" enctype="multipart/form-data">
        <label for="model_choice">Choose a model:</label>
        <select name="model_choice" id="model_choice">
          <option value="gemini-2.0-flash">gemini-2.0-flash</option>
          <option value="gemini-2.0-pro">gemini-2.0-pro</option>
        </select>
        <label for="uploaded_file">Upload a file:</label>
        <input type="file" name="uploaded_file" id="uploaded_file">
        <textarea name="prompt" placeholder="Command (e.g. 'ls -la', 'create test.py')..." autofocus></textarea>
        <button type="submit">Run</button>
    </form>
    <button id="clear-history">Clear History</button>
    <div id="thinking">Thinking...</div>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        const history = document.getElementById('chat-history');
        history.scrollTop = history.scrollHeight;

        document.querySelector('textarea').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                document.querySelector('form').submit();
                document.getElementById('thinking').style.display = 'block';
            }
        });

        document.querySelector('form').addEventListener('submit', function() {
            document.getElementById('thinking').style.display = 'block';
        });

        document.getElementById('clear-history').addEventListener('click', function() {
            fetch('/reset', { method: 'POST' }).then(function() {
                location.reload();
            });
        });

        function renderMarkdown() {
            const agentMessages = document.querySelectorAll('.agent-msg');
            agentMessages.forEach(msg => {
                msg.innerHTML = marked.parse(msg.innerHTML);
            });
        }

        renderMarkdown();
    </script>
</body>
</html>
"""

history_log = []

class GeminiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            history_html = ""
            for role, text in history_log:
                css_class = "user-msg" if role == "USER" else "agent-msg"
                safe_text = (text or "").replace("<", "&lt;").replace(">", "&gt;")
                history_html += f'<div class="msg {css_class}">{safe_text}</div>'

            if not history_log:
                history_html = '<div class="msg agent-msg">System ready. Waiting for instructions...</div>'

            response_html = HTML_TEMPLATE.replace("{{CHAT_HISTORY}}", history_html)
            self.wfile.write(response_html.encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/":
            # Parse the form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']
                         }
            )

            # Extract the model choice
            model_choice = form.getvalue('model_choice')
            print(f"\n[SERVER] Model Choice: {model_choice}")

            # Handle the uploaded file
            if 'uploaded_file' in form and form['uploaded_file'].filename:
                file_item = form['uploaded_file']
                # Generate a unique filename
                timestamp = str(int(time.time()))
                filename = os.path.join(os.getcwd(), f'{timestamp}_{file_item.filename}')

                # Save the file to the current directory
                with open(filename, 'wb') as f:
                    f.write(file_item.file.read())

                print(f"\n[SERVER] Uploaded file: {filename}")

                # (Optional) If the uploaded file is a new persona file, read its contents and update the SYSTEM_INSTRUCTION
                # For now, we'll just print a message
                print("\n[SERVER]  Uploaded file could be a new persona file.  Handling of persona files is not yet implemented.")
            else:
                print("\n[SERVER] No file was uploaded")

            # Extract the user prompt
            user_prompt = form.getvalue('prompt')

            if user_prompt:
                print(f"\n📩 PROMPT: {user_prompt}")
                history_log.append(("USER", user_prompt))
                try:
                    # Create a new chat session with the selected model
                    new_chat_session = client.chats.create(
                        model=model_choice,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            tools=[Bash, Edit, View, Glob, Grep],
                            temperature=0.1,
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                                disable=False,
                                maximum_remote_calls=15
                            )
                        )
                    )

                    response = new_chat_session.send_message(user_prompt)
                    output_text = response.text if response.text else "(No text output)"
                except Exception as e:
                    output_text = f"❌ Error: {str(e)}"

                history_log.append(("GEMINI", output_text))

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        elif self.path == "/reset":
            history_log.clear()
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

def attempt_port_bind(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
        return True
    except OSError:
        return False

def find_available_port():
    ports_to_try = [SERVER_PORT, 8888] + list(range(8081, 8100))
    for port in ports_to_try:
        if attempt_port_bind(port):
            return port
    return None

if __name__ == "__main__":
    print(f"🌍 Working Directory: {os.getcwd()}")

    # --- PORT TAKEOVER LOGIC ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Short timeout for checking
    try:
        sock.bind(('localhost', SERVER_PORT))
    except OSError as e:
        if FORCE_TAKEOVER:
            print(f"Port {SERVER_PORT} is busy. Attempting takeover...")
            try:
                # Find the PID using lsof
                lsof_command = f"lsof -t -i:{SERVER_PORT}"
                result = subprocess.run(lsof_command, shell=True, capture_output=True, text=True)
                pid = int(result.stdout.strip())
                print(f"⚔️  Younger (v4) is displacing Older (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)  # Wait for the socket to release
            except Exception as e:
                print(f"Error during takeover: {e}")
                sys.exit(1)
        else:
            print(f"Port {SERVER_PORT} is busy. Use --force to displace.")
            sys.exit(1)
    finally:
        sock.close()

    # --- PORT SELECTION ---
    PORT = SERVER_PORT #find_available_port()
    #if PORT is None:
    #    print("❌ Error: Could not find an available port.")
    #    sys.exit(1)

    print(f"📡 Serving on Port {PORT}...")
    with socketserver.TCPServer(("", PORT), GeminiHandler) as httpd:
        print(f"✅ Server started on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
