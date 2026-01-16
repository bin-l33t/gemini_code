import os
import re
import json
import shutil
from pathlib import Path

# Config
SOURCE_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
PERSONA_DIR = "extracted_personas"
HYDRATED_DIR = "hydrated_personas"
MAP_FILE = "variable_map_final.json"

def step_1_extract_truth():
    """Scans the source JS for definitive 'var X = "Tool"' definitions."""
    print("--- 1. Extracting Ground Truth from Source ---")
    with open(SOURCE_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # The Rosetta Stone Pattern: var X = "String";
    # We focus on known tool names to reduce false positives
    known_tools = ["Bash", "Grep", "Glob", "View", "Read", "Edit", "Write", "Notebook", "NotebookEdit", "NotebookRead", "StructuredOutput"]
    
    found_map = {}
    
    # Pattern 1: Direct assignment var K9="Bash"
    for tool in known_tools:
        # Regex: var (variable) = "(ToolName)"
        pattern = r'var\s+([a-zA-Z0-9_]+)\s*=\s*"' + tool + r'"'
        matches = re.findall(pattern, content)
        for match in matches:
            print(f"✅ FOUND TRUTH: ${{{match}}} = {tool}")
            found_map[f"${{{match}}}"] = tool

    # Pattern 2: The "StructuredOutput" is often named "EE" or similar in specific contexts
    # We found this in your dragnet earlier, let's keep it if we can't find it via regex
    if "${EE}" not in found_map:
         found_map["${EE}"] = "StructuredOutput" 

    # Save
    with open(MAP_FILE, "w") as f:
        json.dump(found_map, f, indent=2)
    
    return found_map

def step_2_hydrate(variable_map):
    """Hydrates the personas using the verified map."""
    print("\n--- 2. Hydrating Personas ---")
    
    if not os.path.exists(HYDRATED_DIR):
        os.makedirs(HYDRATED_DIR)

    # Load all extracted personas
    for filename in os.listdir(PERSONA_DIR):
        if not filename.endswith(".md"): continue
        
        src_path = os.path.join(PERSONA_DIR, filename)
        dst_path = os.path.join(HYDRATED_DIR, filename)
        
        with open(src_path, "r") as f:
            content = f.read()
            
        # Apply Replacements
        for var_name, real_name in variable_map.items():
            # Escape for regex (e.g., ${A} -> \$\{A\})
            safe_var = re.escape(var_name)
            # Replace ${A} with real_name
            content = re.sub(safe_var, real_name, content)
            
            # Also replace A.prop usage if A is mapped
            # e.g. if ${A} is Bash, we might see A.command. 
            # This is harder to do safely with simple string replacement, 
            # so we focus on the ${A} template literals first.

        with open(dst_path, "w") as f:
            f.write(content)
        print(f"💧 Hydrated {filename}")

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Source file not found: {SOURCE_FILE}")
        return

    # 1. Get Truth
    var_map = step_1_extract_truth()
    
    # 2. Hydrate
    step_2_hydrate(var_map)
    
    print("\n✅ Pipeline Complete. Check 'hydrated_personas/'")

if __name__ == "__main__":
    main()
