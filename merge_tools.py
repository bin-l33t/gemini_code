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
    
    # 1. Load Tools extracted by extract_schemas_full.py
    # In the sacrifice pipeline, this is the main source of truth
    new_extracted = load_json('tools_def.json')
    print(f"✅ Loaded {len(new_extracted)} Extracted Tools (from tools_def.json)")

    # 2. Load Legacy/Browser Tools (Optional - keep if you plan to copy these files over)
    core = load_json('core_tools_reconstructed.json')
    if core: print(f"✅ Loaded {len(core)} Legacy Core Tools")
    
    browser = load_json('gemini_browser_tools.json')
    if browser:
        # Flatten if necessary
        if isinstance(browser[0], list):
            browser = [item for sublist in browser for item in sublist]
        print(f"✅ Loaded {len(browser)} Browser Tools")
    else:
        browser = []

    # 3. Combine
    # Deduplicate by name
    seen_names = set()
    master_list = []
    
    # Prioritize 'new_extracted'
    all_tools = new_extracted + core + browser
    
    for tool in all_tools:
        # Normalize structure (handle 'function' wrapper vs direct object)
        t_def = tool.get('function', tool)
            
        name = t_def.get('name')
        if name and name not in seen_names:
            master_list.append(t_def) 
            seen_names.add(name)
    
    # 4. Save
    with open('master_tool_definitions.json', 'w') as f:
        json.dump(master_list, f, indent=2)
        
    print(f"🎉 Saved {len(master_list)} unique tools to master_tool_definitions.json")

if __name__ == "__main__":
    merge()
