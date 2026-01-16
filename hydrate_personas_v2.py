import json
import os
import re

PERSONAS_DIR = "extracted_personas"
OUTPUT_DIR = "hydrated_personas"
MAP_FILE = "variable_map_master.json"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(MAP_FILE, 'r') as f:
        var_map = json.load(f)

    print(f"--- 💧 Hydrating Personas using {len(var_map)} variables ---")

    files = [f for f in os.listdir(PERSONAS_DIR) if f.endswith(".md")]
    
    for filename in files:
        with open(os.path.join(PERSONAS_DIR, filename), 'r') as f:
            content = f.read()

        # 1. Direct Substitution ${VAR} -> Value
        for var_name, value in var_map.items():
            # Handle keys that might strictly be 'A' vs '${A}'
            clean_key = var_name.replace("${", "").replace("}", "")
            pattern = r"\$\{" + re.escape(clean_key) + r"\}"
            content = re.sub(pattern, str(value), content)

        # 2. Heuristic Cleanup (Optional: remove remaining ${} if they look like artifacts)
        # We leave them for now so the Audit can catch them.

        with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
            f.write(content)
            
        print(f"💧 Hydrated {filename}")

if __name__ == "__main__":
    main()
