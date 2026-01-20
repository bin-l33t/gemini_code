import os
import sys
import subprocess
import glob as glob_module
import http.server
import socketserver
import urllib.parse
import argparse
import tempfile
import shutil
import socket
import signal
import time
import google.generativeai as genai
from google.generativeai import types

# --- Configuration ---
PORT = 8888
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro"
]

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description='Gemini Code Server with Agent Identity')
parser.add_argument('--port', type=int, default=PORT, help='Port to run the server on')
parser.add_argument('--force', action='store_true', help='Force takeover of the port')
args = parser.parse_args()

AGENT_NAME = "Agent"
SERVER_PORT = args.port
OTHER_PORT = 8081 if SERVER_PORT == 8080 else 8080
FORCE_TAKEOVER = args.force

# --- Persona ---
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- Tool Definitions ---

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
    # If command fails with permission error, suggest user check sudoers config; do not attempt interactive sudo.

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

# --- Agent Initialization ---

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

# --- HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Code Console v7</title>
    <style>
        body { font-family: monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; }
        #chat-history { background-color: #252526; padding: 20px; border-radius: 5px; height: 60vh; overflow-y: scroll; border: 1px solid #3c3c3c; margin-bottom: 20px; }
        .user-msg { color: #569cd6; margin-bottom: 10px; }
        .gemini-msg { color: #ce9178; margin-bottom: 20px; white-space: pre-wrap; }
        .controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; background: #2d2d2d; padding: 15px; border-radius: 5px; }
        input[type="text"], select, input[type="file"] { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555; padding: 8px; border-radius: 3px; }
        input[type="text"] { flex-grow: 1; }
        button { background-color: #0e639c; color: white; border: none; padding: 8px 15px; cursor: pointer; border-radius: 3px; }
        button:hover { background-color: #1177bb; }
        .file-upload-label { cursor: pointer; font-size: 0.9em; color: #aaa; }
    </style>
</head>
<body>
    <h1>Gemini Code Console v7</h1>
    
    <div id="chat-history">
        {{CHAT_HISTORY}}
    </div>

    <form action="/" method="POST" enctype="multipart/form-data" class="controls">
        <select name="model">
            {{MODEL_OPTIONS}}
        </select>
        
        <input type="file" name="file" id="file-input">
        
        <input type="text" name="prompt" placeholder="Enter your command or question..." required autofocus>
        <button type="submit">Send</button>
        <button type="button" onclick="window.location.href='/reset'">Reset</button>
    </form>

    <script>
        // Auto-scroll to bottom
        var chatHistory = document.getElementById("chat-history");
        chatHistory.scrollTop = chatHistory.scrollHeight;
    </script>
</body>
</html>
"""

# --- Global State ---
history_log = []

def get_html(current_model=DEFAULT_MODEL):
    """Generates the HTML with history and model options."""
    history_html = ""
    for role, text in history_log:
        css_class = "user-msg" if role == "USER" else "gemini-msg"
        history_html += f"<div class='{css_class}'><strong>{role}:</strong> {text}</div>"
    
    options_html = ""
    for model in AVAILABLE_MODELS:
        selected = "selected" if model == current_model else ""
        options_html += f'<option value="{model}" {selected}>{model}</option>'

    return HTML_TEMPLATE.replace("{{CHAT_HISTORY}}", history_html).replace("{{MODEL_OPTIONS}}", options_html)

def parse_multipart_form_data(body, content_type_header):
    """
    Manually parses multipart/form-data to avoid dependency issues.
    Returns a dictionary of fields and a dictionary of files.
    """
    boundary = content_type_header.split("boundary=")[1].encode()
    parts = body.split(b"--" + boundary)
    
    fields = {}
    files = {}

    for part in parts:
        if not part or part == b"--\r\n": continue
        
        # Split headers and body
        subparts = part.split(b"\r\n\r\n", 1)
        if len(subparts) < 2: continue
        
        headers_raw = subparts[0].decode()
        content = subparts[1].rstrip(b"\r\n")

        # Extract name and filename
        name = None
        filename = None
        
        for line in headers_raw.split("\r\n"):
            if "Content-Disposition" in line:
                params = line.split(";")
                for param in params:
                    if "name=" in param:
                        name = param.split("=")[1].strip('"')
                    if "filename=" in param:
                        filename = param.split("=")[1].strip('"')
        
        if name:
            if filename:
                files[name] = {"filename": filename, "content": content}
            else:
                fields[name] = content.decode()

    return fields, files

class GeminiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/reset':
            global history_log
            history_log = []
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_html().encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers.get('Content-Type', '')
        body = self.rfile.read(content_length)

        prompt = ""
        model = DEFAULT_MODEL
        uploaded_file = None

        # Parse request body
        if 'multipart/form-data' in content_type:
            fields, files = parse_multipart_form_data(body, content_type)
            prompt = fields.get('prompt', '')
            model = fields.get('model', DEFAULT_MODEL)
            if 'file' in files and files['file']['filename']:
                uploaded_file = files['file']
        else:
            # Fallback for standard form (unlikely with new HTML, but safe)
            params = urllib.parse.parse_qs(body.decode('utf-8'))
            prompt = params.get('prompt', [''])[0]
            model = params.get('model', [DEFAULT_MODEL])[0]

        # Update History
        history_log.append(("USER", f"{prompt} " + (f"[Attached: {uploaded_file['filename']}]" if uploaded_file else "")))

        try:
            # Prepare Contents
            contents = [prompt]
            
            # Handle File Upload
            if uploaded_file:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file['filename']}") as tmp:
                    tmp.write(uploaded_file['content'])
                    tmp_path = tmp.name
                
                print(f"Uploading file: {tmp_path}")
                # Cleanup local temp file
                os.unlink(tmp_path)

            # Generate Response
            print(f"Generating with model: {model}")
            response = chat_session.send_message(prompt)
            
            response_text = response.text
            history_log.append(("GEMINI", response_text))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            history_log.append(("GEMINI", error_msg))

        # Redirect back to home
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def attempt_port_bind(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
        return True
    except OSError:
        return False

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
                print(f"⚔️  Younger (v7) is displacing Older (PID: {pid})...")
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

    # --- Server Startup ---
    print(f"Starting Gemini Code Console v7 on port {SERVER_PORT}...")
    with socketserver.TCPServer(("", SERVER_PORT), GeminiHandler) as httpd:
        httpd.serve_forever()
