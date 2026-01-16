# update_map_web_tools.py
import json

# Load existing map
with open("variable_map_final.json", "r") as f:
    data = json.load(f)

# Apply findings from your recent grep session
updates = {
    "${mI}": "WebFetch",
    "${BR}": "WebSearch",
    "${nF5}": "https://code.claude.com/docs/en/claude_code_docs_map.md",
    "${DI2}": "https://platform.claude.com/llms.txt",
    "${aF5}": "claude", # Found in the same grep line
    "${JI2}": "Bash",   # Found in your grep: agentType:"Bash"
}

print(f"--- 🩹 Patching {len(updates)} Web/Doc Variables ---")
for k, v in updates.items():
    print(f"  ✅ Mapping {k} -> {v}")
    data[k] = v

with open("variable_map_final.json", "w") as f:
    json.dump(data, f, indent=2)
    
print("--- 💾 Saved to variable_map_final.json ---")
