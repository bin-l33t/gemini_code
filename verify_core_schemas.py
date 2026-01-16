import re

CLI_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def scan_for_tool_shapes():
    with open(CLI_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    print("--- 🔬 Micro-Scanning for Core Tool Shapes ---")

    # 1. Hunt for the Edit/TextEditor definition
    # We look for "inputSchema" near "view" or "create" or "str_replace"
    print("\n[+] Hunting for 'Edit' or 'TextEditor' Tool Schema:")
    # Look for the specific properties usually found in the Edit tool
    edit_patterns = [
        r'properties:\{command:\{type:"string",enum:\["view","create","str_replace","insert",',
        r'properties:\{command:\{type:"string",enum:\["view","create","replace",',
        r'properties:\{path:\{type:"string".{0,100}file_text'
    ]
    
    found_edit = False
    for pat in edit_patterns:
        matches = re.findall(pat, content)
        if matches:
            print(f"✅ Found Trace: {matches[0][:100]}...")
            found_edit = True
    
    if not found_edit:
        print("❌ Could not pin-point Edit tool structure. It might be dynamic.")

    # 2. Hunt for Bash Tool parameters
    print("\n[+] Hunting for 'Bash' Tool Schema:")
    # We suspect it has a restart parameter or session_id based on previous sniffs
    bash_patterns = [
        r'properties:\{command:\{type:"string".{0,200}restart:\{type:"boolean"',
        r'properties:\{command:\{type:"string".{0,200}session_id'
    ]
    
    for pat in bash_patterns:
        matches = re.findall(pat, content)
        if matches:
            print(f"✅ Found Trace: {matches[0][:100]}...")
            
    # 3. Hunt for the "Repl" or "Notebook" tool
    print("\n[+] Hunting for Notebook/Repl Tool:")
    repl_patterns = [
        r'inputSchema:\{type:"object",properties:\{code:\{type:"string"'
    ]
    for pat in repl_patterns:
        matches = re.findall(pat, content)
        if matches:
            print(f"✅ Found Trace: {matches[0][:100]}...")

if __name__ == "__main__":
    scan_for_tool_shapes()
