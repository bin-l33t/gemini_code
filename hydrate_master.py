# Save as: hydrate_master.py
import os
import json
import re

def hydrate():
    print("--- 💧 Running Master Hydration ---")
    
    with open("master_variable_map.json", "r") as f:
        var_map = json.load(f)
    
    # Sort keys by length (descending) to prevent partial replacement
    # e.g. replace ${A.name} before ${A}
    sorted_vars = sorted(var_map.keys(), key=len, reverse=True)
    
    input_dir = "extracted_personas"
    output_dir = "hydrated_personas"
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith(".md")]
    
    for filename in files:
        with open(os.path.join(input_dir, filename), "r") as f:
            content = f.read()
            
        original_content = content
        
        for key in sorted_vars:
            val = var_map[key]
            # Escape key for regex (handle $, ., {, })
            pattern = re.escape(key)
            content = re.sub(pattern, val, content)
            
        # Write Result
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(content)
            
        if content != original_content:
            print(f"💧 Hydrated {filename}")
        else:
            print(f"➖ No changes in {filename} (Check if map covers this file)")

if __name__ == "__main__":
    hydrate()
