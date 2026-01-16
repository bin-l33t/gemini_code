import re
import json

# We are looking for patterns like: const A = "ReadLocalFile"; or properties { A: "..." }
# This is a heuristic approach based on your deep_scan results.

TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def crack_variables():
    with open(TARGET_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Dictionary to store our findings
    var_map = {}

    print("--- 🕵️‍♀️ Cracking Variable Map ---")

    # 1. Look for the Planner Tool Name (mW.name / nu)
    # You found this in hunter.py, but let's formalize it.
    if "mW.name" not in var_map:
        var_map["mW.name"] = "TodoWrite" # Hardcoded based on your previous 'hunter.py' success

    # 2. Look for Tool Definitions where the name is a variable
    # Pattern: name:V9("Grep") or name:A where A is defined nearby
    # This is hard in minified code. We will try to infer from the *usage* in the extracted schema errors you saw earlier.
    
    # Based on your grep output:
    # readFileSync(A,Q) -> implies A might be "path" and Q "encoding" in the function args, 
    # BUT in the Prompt, ${A} refers to the TOOL NAME.
    
    # Let's try to map standard CLI tool names to the variables found in Deep Scan
    # The most frequent variables in deep_scan were A, Q, B, Y, G.
    # The most common tools in a coding agent are: View, Edit, Bash/Run, Grep, Ls.

    common_tools = {
        "View": ["read", "cat", "view", "file_read"],
        "Edit": ["write", "edit", "replace", "str_replace"],
        "Bash": ["command", "run", "exec", "bash"],
        "Glob": ["ls", "find", "glob", "list"],
        "Grep": ["grep", "search", "rg"]
    }

    print("⚠️  Manual Override Required for Minified Variables.")
    print("We will infer mappings based on Prompt Context in the next step.")
    
    # We will create a map based on context we see in the prompt files
    # This is a 'best guess' map to start the agent.
    
    inferred_map = {
        "${A}": "View",       # High frequency, usually the primary read tool
        "${Q}": "Edit",       # High frequency, usually the write tool
        "${mW.name}": "Planner",
        "${EE}": "StructuredOutput", # Confirmed
        "${b3}": "Notebook",  # Often appears with planner
        "${C3}": "Bash",      # Execution tool
        "${gI}": "Grep",      # Search tool
        "${BI}": "LS",        # List files
    }

    print(f"✅ Generated Heuristic Map: {json.dumps(inferred_map, indent=2)}")
    
    with open('variable_map.json', 'w') as f:
        json.dump(inferred_map, f, indent=2)

if __name__ == "__main__":
    crack_variables()
