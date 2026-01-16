import re
import json

SOURCE_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def extract_core_tools():
    with open(SOURCE_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    print("--- 🕵️‍♀️ Surgical Extraction for Core Tools ---")

    # The core tools often look like: name:"Bash",description:"...",inputSchema:{...}
    # We will look for the specific names we know are missing.
    targets = ["Bash", "Glob", "Grep", "TextEditor", "Edit"]
    
    tools = []

    for target in targets:
        print(f"Scanning for {target}...")
        # Regex explanation:
        # name:"TARGET"  -> Find the name
        # .{0,500}       -> Allow some characters in between (aliases, etc)
        # inputSchema:   -> Find the schema start
        # (\{.*?\})      -> Capture the JSON object (non-greedy)
        # Note: This is a rough heuristic; we might need to balance braces if complex.
        
        pattern = r'name:"' + target + r'".{0,1000}inputSchema:(\{.*?\})\,([a-zA-Z]+):'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        for m in matches:
            raw_schema = m.group(1)
            # Try to fix unquoted keys common in minified JS
            fixed_schema = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', raw_schema)
            # Fix single quotes to double quotes
            fixed_schema = fixed_schema.replace("'", '"')
            
            try:
                # Attempt to parse to verify validity
                # We often have issues with "function(x){...}" in JS objects, so this is risky
                # But let's try to grab the raw string first.
                tools.append({
                    "name": target,
                    "raw_schema": raw_schema,
                    "fixed_attempt": fixed_schema
                })
                print(f"  ✅ Found candidate for {target}!")
            except Exception as e:
                print(f"  ⚠️ Found {target} but failed to parse: {e}")

    # Output what we found so we can manually clean it or use Gemini to fix it
    with open("core_tools_raw.json", "w") as f:
        json.dump(tools, f, indent=2)
    
    print(f"--- Saved {len(tools)} candidates to core_tools_raw.json ---")
    print("Next Step: Use 'python heal_core.py' (you need to create this) to fix the JSON syntax.")

if __name__ == "__main__":
    extract_core_tools()
