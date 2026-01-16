# merge_tools.py
import json
import os

def load_json(path):
    if not os.path.exists(path):
        print(f"⚠️ Warning: {path} not found. Skipping.")
        return []
    with open(path, 'r') as f:
        return json.load(f)

def merge():
    print("--- 🔗 Merging Tool Definitions ---")
    
    # 1. Load Core Tools (Bash, Grep, etc.)
    core = load_json('core_tools_reconstructed.json')
    print(f"✅ Loaded {len(core)} Core Tools")

    # 2. Load Browser/Web Tools (MCP, Navigation)
    # The browser tools might be a list of lists or a flat list, let's flatten if needed
    raw_browser = load_json('gemini_browser_tools.json')
    browser = []
    
    # Handle potential list-of-lists structure from extraction
    if raw_browser and isinstance(raw_browser[0], list):
        for sublist in raw_browser:
            browser.extend(sublist)
    else:
        browser = raw_browser
        
    print(f"✅ Loaded {len(browser)} Browser Tools")

    # 3. Combine
    # Deduplicate by name just in case
    seen_names = set()
    master_list = []
    
    for tool in core + browser:
        # Normalize structure (handle 'function' wrapper vs direct object)
        if 'function' in tool: 
            t_def = tool['function']
        else:
            t_def = tool
            
        name = t_def.get('name')
        if name and name not in seen_names:
            # Standardize for Gemini (remove 'function' wrapper if present for Pydantic/Gemini compat)
            master_list.append(t_def) 
            seen_names.add(name)
    
    # 4. Save
    with open('master_tool_definitions.json', 'w') as f:
        json.dump(master_list, f, indent=2)
        
    print(f"🎉 Saved {len(master_list)} unique tools to master_tool_definitions.json")

if __name__ == "__main__":
    merge()
