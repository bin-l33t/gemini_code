import json
import os
import re

def fix_agent_code_writer():
    # 1. Update the Variable Map
    map_path = "variable_map_master.json"
    
    # Check if map exists, if not try sanitized/final versions
    if not os.path.exists(map_path):
        map_path = "variable_map_final.json"
    
    print(f"--- 🩹 Patching Variable Map: {map_path} ---")
    
    with open(map_path, "r") as f:
        var_map = json.load(f)
    
    # Define the missing variable found in agent_code_writer.md
    # "LocalAgentTask" is the standard internal name for the agent-spawner
    var_map["${AEA.name}"] = "LocalAgentTask"
    
    with open(map_path, "w") as f:
        json.dump(var_map, f, indent=2)
    print(f"✅ Added ${{AEA.name}} -> LocalAgentTask")

    # 2. Re-Hydrate agent_code_writer.md
    target_file = "hydrated_personas/agent_code_writer.md"
    if not os.path.exists(target_file):
        # Fallback if the file hasn't been renamed from persona_990.md yet
        target_file = "gemini_code_personas/persona_990.md"
        
    if os.path.exists(target_file):
        print(f"--- 💧 Re-hydrating {target_file} ---")
        with open(target_file, "r") as f:
            content = f.read()
        
        # Apply the fix directly
        new_content = content.replace("${AEA.name}", "LocalAgentTask")
        
        with open(target_file, "w") as f:
            f.write(new_content)
            
        print("✅ File patched.")
    else:
        print(f"❌ Could not find {target_file} to patch.")

    # 3. Verify
    print("--- 🔍 Verification ---")
    if os.path.exists(target_file):
        with open(target_file, "r") as f:
            if "${" in f.read():
                print("❌ WARNING: Artifacts still remain.")
            else:
                print("✅ SUCCESS: File is clean.")

if __name__ == "__main__":
    fix_agent_code_writer()
