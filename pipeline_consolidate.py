import json
import os
import re

# 1. Load the Truth Map
with open("variable_map_final.json", "r") as f:
    var_map = json.load(f)

# 2. Add HEURISTIC overrides for the remaining dirty variables
# These are variables that are likely dynamic at runtime, so we map them to defaults.
overrides = {
    "${A.planFilePath}": "PLAN.md",
    "${M$.name}": "Planner",
    "${nF5}": "https://docs.anthropic.com/en/docs/intro-to-claude", # Fallback for docs
    "${DI2}": "https://docs.anthropic.com/en/api/getting-started",
    "${mI}": "WebFetch", 
    "${BR}": "WebSearch",
    # Fix the Planner "Edit" ambiguity
    "Use the Edit tool": "Use the Write tool (to overwrite) or Edit tool (to modify)",
}

print(f"--- 🔄 Consolidating Pipeline with {len(var_map) + len(overrides)} mappings ---")

def hydrate_file(input_path, output_path):
    with open(input_path, "r") as f:
        content = f.read()
    
    # Apply Truth Map
    for k, v in var_map.items():
        content = content.replace(k, v)
        
    # Apply Overrides
    for k, v in overrides.items():
        content = content.replace(k, v)
    
    # Regex Fix for ${A.*} patterns that might remain
    # content = re.sub(r'\$\{A\.[a-zA-Z]+\}', 'runtime_context', content)

    with open(output_path, "w") as f:
        f.write(content)
    print(f"✅ Hydrated {output_path}")

# Run on critical agents
personas = [
    ("extracted_personas/agent_engineer.md", "hydrated_personas/agent_engineer.md"),
    ("extracted_personas/agent_planner.md", "hydrated_personas/agent_planner.md"),
    ("extracted_personas/persona_765.md", "hydrated_personas/agent_architect_full.md"), # 765 is often the full architect
    ("extracted_personas/persona_768.md", "hydrated_personas/agent_commit.md"),
]

for src, dst in personas:
    if os.path.exists(src):
        hydrate_file(src, dst)
    else:
        print(f"⚠️ Source missing: {src}")

print("\n--- Pipeline Consolidated. Ready for Dry Run. ---")
