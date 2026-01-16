import json
import os

# Configuration
INPUT_FILE = 'variable_map_master.json'  # Consumes output from merge_hunt_results.py
OUTPUT_FILE = 'variable_map_sanitized.json'

def main():
    print(f"--- 🧹 Sanitizing Variable Map ({INPUT_FILE}) ---")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Ensure merge_hunt_results.py ran successfully.")
        return

    # Load current map
    with open(INPUT_FILE, 'r') as f:
        vmap = json.load(f)

    # List of generic minified variables that are DANGEROUS to map globally
    # These often cause false positives in hydration (e.g. replacing every "A" or "B")
    BLACKLIST = ["${A}", "${Q}", "${B}", "${G}", "${Z}", "${Y}", "${E}", "${I}"]

    new_map = {}
    removed_count = 0
    
    for k, v in vmap.items():
        if k in BLACKLIST:
            # print(f"  ❌ Removing generic variable: {k} -> {v}") # Uncomment for verbose logs
            removed_count += 1
        else:
            new_map[k] = v

    print(f"ℹ️  Removed {removed_count} generic/risky short variables.")

    # Ensure our hard-won truths are present (Manual Overrides for Safety)
    # These are the critical tools we absolutely need for the agent to function
    overrides = {
        "${K9}": "Bash",
        "${f3}": "Edit",
        "${C3}": "Read",
        "${gI}": "Glob",
        "${BI}": "Grep",
        "${eZ}": "Write",
        "${Tq}": "NotebookEdit",
        "${mW.name}": "TodoWrite" # Planner tool
    }

    added_count = 0
    for k, v in overrides.items():
        if k not in new_map:
            # print(f"  ➕ Adding missing core tool: {k} -> {v}")
            new_map[k] = v
            added_count += 1
        else:
            # Enforce override if it exists but is different?
            # For now, we trust the map unless it's missing, but we could enforce here.
            pass

    if added_count > 0:
        print(f"ℹ️  Restored {added_count} critical tool definitions.")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(new_map, f, indent=2)

    print(f"✅ Map Sanitized. Saved to {OUTPUT_FILE} (Total keys: {len(new_map)})")

if __name__ == "__main__":
    main()
