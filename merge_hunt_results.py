import json
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def main():
    print("--- 🔄 Merging Smart Hunt Results into Master Map ---")
    
    # Load the different maps you've generated
    heuristic_map = load_json('variable_map.json')
    sanitized_map = load_json('variable_map_sanitized.json')
    smart_map = load_json('smart_map.json') # This contains the gold from smart_hunt.py
    
    # Priority: Smart Hunt > Sanitized > Heuristic
    final_map = heuristic_map.copy()
    final_map.update(sanitized_map)
    final_map.update(smart_map)

    # Manual Overrides based on your 'smart_hunt' logs that might not be in the JSON yet
    # These are hard-coded based on the logs you provided in the context
    overrides = {
        "${K9}": "Bash",
        "${gI}": "Glob",
        "${BI}": "Grep",
        "${C3}": "Read",
        "${f3}": "Edit",
        "${eZ}": "Write",
        "${Tq}": "NotebookEdit",
        "${mI}": "WebFetch",
        "${BR}": "WebSearch",
        "${nu}": "TodoWrite",
        "${Tb}": "MCPSearch",
        "${YJ1}": "ExitPlanMode",
        "${qF1}": "EnterPlanMode",
        "${VF1}": "KillShell",
        "${uF}": "Skill",
        "${nF5}": "https://code.claude.com/docs/en/claude_code_docs_map.md",
        "${DI2}": "https://platform.claude.com/llms.txt"
    }
    
    print(f"Applying {len(overrides)} manual overrides from log analysis...")
    final_map.update(overrides)

    # Save
    with open('variable_map_master.json', 'w') as f:
        json.dump(final_map, f, indent=2)
        
    print(f"✅ Master Map Saved with {len(final_map)} definitions.")

if __name__ == "__main__":
    main()
