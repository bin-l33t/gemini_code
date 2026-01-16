import json

# Load current map
with open('variable_map_final.json', 'r') as f:
    vmap = json.load(f)

print("--- 🧹 Sanitizing Variable Map ---")

# List of generic minified variables that are DANGEROUS to map globally
BLACKLIST = ["${A}", "${Q}", "${B}", "${G}", "${Z}", "${Y}"]

new_map = {}
for k, v in vmap.items():
    if k in BLACKLIST:
        print(f"❌ Removing generic variable: {k} -> {v}")
    else:
        new_map[k] = v

# Ensure our hard-won truths are present
overrides = {
    "${K9}": "Bash",
    "${f3}": "Edit",
    "${C3}": "Read",
    "${gI}": "Glob",
    "${BI}": "Grep",
    "${eZ}": "Write",
    "${mW.name}": "TodoWrite" # Planner tool
}

for k, v in overrides.items():
    if k not in new_map:
        print(f"➕ Adding missing core tool: {k} -> {v}")
    new_map[k] = v

with open('variable_map_sanitized.json', 'w') as f:
    json.dump(new_map, f, indent=2)

print("--- ✅ Map Sanitized. Saved to variable_map_sanitized.json ---")
