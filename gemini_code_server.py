import os
import sys
import subprocess
import glob as glob_module
import http.server
import socketserver
import urllib.parse
from google import genai
from google.genai import types

# --- Configuration ---
PORT = 8888
PERSONA_FILE = "hydrated_personas/agent_engineer.md"
MODEL_ID = "gemini-2.0-flash"

# --- 1. Tool Implementations (Based on master_tool_definitions.json) ---

def Bash(command: str):
    """Executes a command in the bash shell. Use this to run system commands or scripts."""
    print(f"\n[SERVER] ⚡ Executing Bash: {command}")
    try:
        # Timeout set to 30s to prevent hangs
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
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"[SERVER] ✅ File written ({len(content)} chars).")
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
    print(f"\n[SERVER] 🔍 Globbing: {pattern}")
    try:
        files = glob_module.glob(pattern, recursive=True)
        return "\n".join(files) if files else "No files found."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def Grep(pattern: str, path: str):
    """Searches files for a pattern using grep."""
    print(f"\n[SERVER] 🔦 Grepping '{pattern}' in {path}")
    try:
        # Using subprocess for efficient grepping
        cmd = ["grep", "-r", pattern, path]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        return result.stdout if result.stdout else "No matches found."
    except Exception as e:
        return f"Error executing grep: {str(e)}"

# --- 2. Agent Initialization ---

print("🤖 INITIALIZING GEMINI CODE SERVER...")

if not os.path.exists(PERSONA_FILE):
    print(f"❌ Error: Persona file {PERSONA_FILE} not found. Ensure you are in the correct directory.")
    sys.exit(1)

with open(PERSONA_FILE, "r") as f:
    SYSTEM_INSTRUCTION = f.read()
print(f"✅ Loaded Persona: {PERSONA_FILE}")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Global chat session to maintain context
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

class GeminiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head>
                <title>Gemini Code Server</title>
                <style>
                    body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    textarea { width: 100%; height: 100px; background: #252526; color: #fff; border: 1px solid #3c3c3c; padding: 10px; }
                    button { background: #0e639c; color: white; border: none; padding: 10px 20px; cursor: pointer; margin-top: 10px;}
                    button:hover { background: #1177bb; }
                    #response { white-space: pre-wrap; margin-top: 20px; background: #2d2d2d; padding: 15px; border: 1px solid #3c3c3c; }
                    .user-msg { color: #4ec9b0; font-weight: bold; }
                    .agent-msg { color: #ce9178; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Gemini Code Server</h1>
                    <form method="POST" action="/">
                        <textarea name="prompt" placeholder="Enter your instructions (e.g., 'ls current dir', 'create a flask app')..."></textarea><br>
                        <button type="submit">Execute Mission</button>
                    </form>
                    <div id="response"></div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            user_prompt = params.get('prompt', [''])[0]

            if user_prompt:
                print(f"\n📩 RECEIVED PROMPT: {user_prompt}")
                try:
                    response = chat_session.send_message(user_prompt)
                    output_text = response.text
                except Exception as e:
                    output_text = f"❌ Error processing request: {str(e)}"
            else:
                output_text = "⚠️ Empty prompt received."

            # Simple HTML response with the result
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Escape HTML for display
            safe_output = output_text.replace("<", "&lt;").replace(">", "&gt;")
            safe_prompt = user_prompt.replace("<", "&lt;").replace(">", "&gt;")
            
            html = f"""
            <html>
            <head>
                <title>Gemini Code Server</title>
                <style>
                    body {{ font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    textarea {{ width: 100%; height: 100px; background: #252526; color: #fff; border: 1px solid #3c3c3c; padding: 10px; }}
                    button {{ background: #0e639c; color: white; border: none; padding: 10px 20px; cursor: pointer; margin-top: 10px;}}
                    .result-box {{ white-space: pre-wrap; margin-top: 20px; background: #2d2d2d; padding: 15px; border: 1px solid #3c3c3c; }}
                    a {{ color: #4ec9b0; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Gemini Code Server</h1>
                    <p><a href="/">&lt; Back to Console</a></p>
                    <div class="result-box">
                        <strong>USER:</strong> {safe_prompt}<br><br>
                        <strong>GEMINI:</strong><br>{safe_output}
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

# --- 4. Main Execution ---

if __name__ == "__main__":
    # Ensure we are in the sacrifice directory or compatible env
    print(f"🌍 Working Directory: {os.getcwd()}")
    print(f"📡 Serving on Port {PORT}...")
    
    with socketserver.TCPServer(("", PORT), GeminiHandler) as httpd:
        print(f"✅ Server is Live! Access via http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopping...")
            httpd.server_close()
