import re
import json
import os

# Configuration
TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
OUTPUT_FILE = "tools_def.json"

def extract_balanced_object(text, start_index):
    """
    Extracts a JSON-like object starting from a specific index by counting braces.
    Returns the full string of the object.
    """
    stack = 0
    found_start = False
    obj_start = -1
    
    for i in range(start_index, len(text)):
        char = text[i]
        
        if char == '{':
            if not found_start:
                obj_start = i
                found_start = True
            stack += 1
        elif char == '}':
            stack -= 1
        
        if found_start and stack == 0:
            return text[obj_start : i+1]
            
    return None

def clean_js_object_to_json(js_str):
    """
    Converts a loose Javascript object string to valid JSON.
    1. Quotes unquoted keys (e.g., type: "object" -> "type": "object")
    2. Removes trailing commas.
    """
    # 1. Quote keys: Look for word chars followed by colon, preceded by { or ,
    # We use a specific list of known schema keys to be safer, plus a generic fallback
    # Generic regex: match a key that isn't in quotes
    # Pattern: (Start of string or , or {) followed by whitespace, then key, then :
    
    # Preliminary cleanup: remove newlines to make regex easier
    cleaned = js_str.replace('\n', ' ')
    
    # Regex to quote keys. 
    # Matches: { key: or , key: 
    # We execute this loop until no more changes are made to handle nested structures
    prev = ""
    curr = cleaned
    
    # Simple pass: Quote alphanumeric keys
    # Warning: This is a heuristic. It assumes keys are alphanumeric.
    curr = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', curr)
    
    # 2. Fix single quotes to double quotes for strings (if any)
    # This is risky if the string contains double quotes, but necessary for some JS
    # Helper: specific fix for 'interactive' enum
    curr = curr.replace("'interactive'", '"interactive"').replace("'all'", '"all"')
    
    try:
        return json.loads(curr)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON Parse Error on snippet: {curr[:50]}... Error: {e}")
        return None

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"❌ Error: Could not find {TARGET_FILE}")
        return

    print(f"--- 📖 Reading {TARGET_FILE} ---")
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strategy: Find 'inputSchema:' positions
    # Then look backwards for the tool name
    
    matches = [m.start() for m in re.finditer(r'inputSchema\s*:', content)]
    print(f"✅ Found {len(matches)} tool definitions.")

    tools = []
    
    for idx in matches:
        # 1. Extract Schema
        # The Schema starts at the first '{' after 'inputSchema:'
        schema_start_search = content.find('{', idx)
        if schema_start_search == -1:
            continue
            
        raw_schema = extract_balanced_object(content, schema_start_search)
        if not raw_schema:
            print("❌ Failed to extract balanced object for a match.")
            continue
            
        schema_json = clean_js_object_to_json(raw_schema)
        
        # 2. Extract Name
        # Look backwards 200 chars for 'name:"toolname"' or 'name: "toolname"'
        # Or look for the parent object structure
        snippet_before = content[max(0, idx-300) : idx]
        
        # Regex for name:"..." or name: "..."
        name_match = re.search(r'name\s*:\s*"([a-zA-Z0-9_]+)"', snippet_before)
        if not name_match:
             # Try single quotes
             name_match = re.search(r"name\s*:\s*'([a-zA-Z0-9_]+)'", snippet_before)
        
        tool_name = name_match.group(1) if name_match else "unknown_tool"
        
        if schema_json:
            print(f"  📎 Extracted: {tool_name}")
            tools.append({
                "name": tool_name,
                "inputSchema": schema_json
            })

    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tools, f, indent=2)
    
    print(f"\n✅ Successfully saved {len(tools)} tools to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
