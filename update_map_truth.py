import re
import json
import os

# Configuration
CLI_PATH = "node_modules/@anthropic-ai/claude-code/cli.js"
MAP_FILE = "variable_map.json"

# The specific tool names we are hunting for in the minified code
TARGET_TOOLS = [
    "Bash", "Grep", "Glob", "View", "Edit", "Read", "Write", 
    "LS", "Todo", "Planner", "Notebook", "NotebookEdit", 
    "NotebookRead", "NotebookCell"
]

def update_variable_map():
    print(f"--- 🕵️‍♀️  Scanning {CLI_PATH} for definitive definitions ---")
    
    if not os.path.exists(CLI_PATH):
        print(f"❌ Error: Could not find {CLI_PATH}")
        return

    with open(CLI_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex explanation:
    # var\s+       -> matches "var "
    # ([a-zA-Z0-9_$]+) -> Capture Group 1: The variable name (e.g., K9, gI)
    # \s*=\s* -> matches " = " (with optional whitespace)
    # "([^"]+)"    -> Capture Group 2: The value inside quotes
    pattern = re.compile(r'var\s+([a-zA-Z0-9_$]+)\s*=\s*"([^"]+)"')
    
    matches = pattern.findall(content)
    
    new_mappings = {}
    
    for var_name, value in matches:
        # We only care if the value matches one of our known Tool Names
        if value in TARGET_TOOLS:
            key = f"${{{var_name}}}" # Format as ${VAR}
            new_mappings[key] = value
            print(f"✅ FOUND: var {var_name} = \"{value}\" -> Mapping {key} to {value}")

    # Load existing map
    current_map = {}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r") as f:
            try:
                current_map = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Existing map was corrupt, starting fresh.")

    # Update map (New definitive values overwrite old heuristics)
    print("\n--- 🔄 Merging into variable_map.json ---")
    changes_count = 0
    for key, value in new_mappings.items():
        if current_map.get(key) != value:
            print(f"   📝 Updating {key}: {current_map.get(key, '(new)')} -> {value}")
            current_map[key] = value
            changes_count += 1
    
    if changes_count == 0:
        print("   ✨ No changes needed. Map was already correct.")
    else:
        # Save
        with open(MAP_FILE, "w") as f:
            json.dump(current_map, f, indent=4)
        print(f"   💾 Saved {changes_count} updates to {MAP_FILE}")

if __name__ == "__main__":
    update_variable_map()
