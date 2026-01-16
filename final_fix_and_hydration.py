import json
import os
import re

# 1. Define the High-Confidence Variable Map based on your trace logs
# We are overriding the automated guesses with the "Hard Evidence" found in traces.
CORRECT_MAP = {
    "${mW.name}": "Todo",          # Found in planner context
    "${EE}": "StructuredOutput",   # Confirmed exit strategy
    "${K9}": "Bash",               # Found: var K9="Bash"
    "${gI}": "Glob",               # Found: var gI="Glob"
    "${BI}": "Grep",               # Found: var BI="Grep"
    "${f3}": "Edit",               # Found: var f3="Edit"
    "${eZ}": "Write",              # Found: var eZ="Write"
    "${C3}": "Read",               # CORRECTION: "Use ${C3} to read file contents" -> Read
    "${b3}": "Notebook",           # Notebook tool
    "${A}": "View",                # Reverting A to View/Read context for safety
    "${Q}": "utf-8"                # Encoding default
}

def hydrate_file(filepath, mapping):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for var, replacement in mapping.items():
        # Escape the variable for regex (e.g., ${A} -> \$\{A\})
        pattern = re.escape(var)
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        print(f"✅ Hydrated {os.path.basename(filepath)}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"➖ No changes in {os.path.basename(filepath)}")

def main():
    print("--- 🩹 Applying Surgical Fixes to Variable Map ---")
    
    # Save this map for the App to use
    with open('final_variable_map.json', 'w') as f:
        json.dump(CORRECT_MAP, f, indent=2)
    
    personas_dir = "extracted_personas"
    if not os.path.exists(personas_dir):
        print(f"❌ Directory {personas_dir} not found.")
        return

    print(f"--- Hzdrating Personas in {personas_dir} ---")
    files = [f for f in os.listdir(personas_dir) if f.endswith(".md")]
    
    for filename in files:
        hydrate_file(os.path.join(personas_dir, filename), CORRECT_MAP)

if __name__ == "__main__":
    main()
