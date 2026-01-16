# Save as: unify_assets.py
import json
import glob
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def main():
    print("--- 🔄 Unifying Assets into Master Truth ---")

    # 1. MERGE VARIABLE MAPS
    # Priority: Manual Fixes > Smart Hunt > Original Map
    base_map = load_json("variable_map.json")
    smart_map = load_json("smart_map.json")
    final_map = load_json("variable_map_final.json")
    sanitized_map = load_json("variable_map_sanitized.json")

    # Hardcoded Critical Fixes (from your previous session findings)
    critical_fixes = {
        "${A.planFilePath}": "PLAN.md",
        "${M$.name}": "update_plan",
        "${A$.name}": "Edit",
        "${Q$.name}": "Edit",
        "${$Y}": "Ask",
        "${mS.agentType}": "Planner",
        "${nF5}": "https://code.claude.com/docs/en/claude_code_docs_map.md",
        "${DI2}": "https://platform.claude.com/llms.txt",
        "${mI}": "WebFetch",
        "${BR}": "WebSearch",
        "${K9}": "Bash",
        "${BI}": "Grep",
        "${gI}": "Glob",
        "${C3}": "Read",
        "${f3}": "Edit",
        "${eZ}": "Write",
        "${mW.name}": "TodoWrite"
    }

    master_map = base_map.copy()
    master_map.update(smart_map)
    master_map.update(final_map)
    master_map.update(sanitized_map)
    master_map.update(critical_fixes) # Highest priority

    with open("master_variable_map.json", "w") as f:
        json.dump(master_map, f, indent=2)
    print(f"✅ Saved master_variable_map.json with {len(master_map)} definitions.")

    # 2. MERGE TOOL DEFINITIONS
    # We need to ensure Bash, Edit, etc. are present for the Audit to pass.
    core_tools = load_json("core_tools_reconstructed.json")
    web_tools = load_json("gemini_browser_tools.json")
    
    # Flatten list of lists if necessary (web tools sometimes nested)
    flat_web = []
    if isinstance(web_tools, list):
        for item in web_tools:
            if isinstance(item, list):
                flat_web.extend(item)
            else:
                flat_web.append(item)
    else:
        flat_web = list(web_tools.values())

    master_tools = core_tools + flat_web
    
    # Deduplicate by name
    unique_tools = {}
    for tool in master_tools:
        if "name" in tool: # Some might be raw schemas
            # Fix naming for Gemini (Gemini prefers snake_case or specific names, but we keep original for now)
            unique_tools[tool["name"]] = tool
        elif "function" in tool and "name" in tool["function"]: # Gemini format
             unique_tools[tool["function"]["name"]] = tool

    with open("master_tool_definitions.json", "w") as f:
        json.dump(list(unique_tools.values()), f, indent=2)
    print(f"✅ Saved master_tool_definitions.json with {len(unique_tools)} tools.")

if __name__ == "__main__":
    main()
