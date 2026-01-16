import json

# Load existing map
try:
    with open("variable_map.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

# OVERRIDE with facts derived from your grep logs
updates = {
    "${A}": "path",          # Evidence: existsSync(${A}), readFileSync(${A})
    "${Q}": "encoding",      # Evidence: readFileSync(A, {encoding: Q})
    "${mW.name}": "TodoWrite", # Confirmed by your hunter.py
    "${EE}": "StructuredOutput", # Confirmed by your brute force
    "${gI}": "grep_tool",    # Likely based on context
    "${BI}": "ls_tool",      # Likely based on context
    "${b3}": "Notebook",
    "${C3}": "Bash",
}

data.update(updates)

print("--- 🗺️  Applying Logic-Based Map Updates ---")
for k, v in updates.items():
    print(f"✅ Fixed: {k} -> {v}")

with open("variable_map.json", "w") as f:
    json.dump(data, f, indent=2)
