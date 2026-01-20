import os
import sys
import http.server
import socketserver
import urllib.parse
import argparse
import tempfile
import shutil
import google.generativeai as genai
#from google import types

# --- Configuration ---
PORT = 8082
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro"
]

# --- HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Code Console v5</title>
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
    <h1>Gemini Code Console v5</h1>
    
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
client = None

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
            # Initialize Client
            # Note: We re-init or use a singleton. For simplicity/statelessness, 
            # we use the client to generate content directly.
            global client
            if not client:
                client = genai.Client()

            # Prepare Contents
            contents = [prompt]
            
            # Handle File Upload
            if uploaded_file:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file['filename']}") as tmp:
                    tmp.write(uploaded_file['content'])
                    tmp_path = tmp.name
                
                print(f"Uploading file: {tmp_path}")
                try:
                    # Upload to Gemini File API
                    gemini_file = client.files.upload(file=tmp_path)
                    contents.insert(0, gemini_file)
                finally:
                    # Cleanup local temp file
                    os.unlink(tmp_path)

            # Generate Response
            print(f"Generating with model: {model}")
            response = client.generate_content(
                model=model,
                contents=contents
            )
            
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    print(f"Starting Gemini Code Console v5 on port {args.port}...")
    with socketserver.TCPServer(("", args.port), GeminiHandler) as httpd:
        httpd.serve_forever()
