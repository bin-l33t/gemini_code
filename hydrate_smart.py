# hydrate_smart.py
import re
import json
import glob
import os

def smart_hydrate():
    # Load the map
    with open("variable_map_final.json", "r") as f:
        var_map = json.load(f)

    # Sort keys by length (descending) to prevent partial replacement
    # e.g. replace ${A.planFilePath} before ${A}
    sorted_keys = sorted(var_map.keys(), key=len, reverse=True)

    print(f"--- 💧 Smart Hydration (Handling dots and nested vars) ---")
    
    files = glob.glob("extracted_personas/*.md")
    os.makedirs("hydrated_personas", exist_ok=True)

    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r") as f:
            content = f.read()
        
        original_content = content
        
        # Robust replacement loop
        for key in sorted_keys:
            # We look for the key exactly as it appears in the map (e.g. "${A.planFilePath}")
            # We assume the map keys ALREADY contain the ${} wrapper based on your previous logs
            # If your map keys are just "A.planFilePath", we adjust:
            
            clean_key = key
            if not key.startswith("${"):
                search_pattern = r"\$\{" + re.escape(key) + r"\}"
            else:
                search_pattern = re.escape(key)
                
            replacement = var_map[key]
            
            # Perform substitution
            content = re.sub(search_pattern, replacement, content)

        if content != original_content:
            print(f"✅ Hydrated: {filename}")
        else:
            print(f"➖ No changes: {filename}")
            
        with open(f"hydrated_personas/{filename}", "w") as f:
            f.write(content)

if __name__ == "__main__":
    smart_hydrate()
