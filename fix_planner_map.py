import json

# Load the sanitized map
try:
    with open("variable_map_sanitized.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

# Apply Logical Fixes based on "Snipe" evidence
updates = {
    "${A.planFilePath}": "PLAN.md",
    "${M$.name}": "update_plan",
    "${A$.name}": "Edit",
    "${Q$.name}": "Edit",
    "${$Y}": "Ask",
    "${mS.agentType}": "Planner", # Context guess: "using the Planner tool"
}

print(f"--- 🩹 Applying {len(updates)} Fixes to Variable Map ---")
for k, v in updates.items():
    print(f"   Mapping {k} -> {v}")
    data[k] = v

# Save
with open("variable_map_sanitized.json", "w") as f:
    json.dump(data, f, indent=2)

print("--- ✅ Map Updated. Ready for Re-Hydration. ---")
