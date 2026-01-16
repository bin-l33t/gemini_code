# pipeline_master.py
import subprocess
import sys
import time

def run_step(script_name, description):
    print(f"\n🚀 STEP: {description} ({script_name})")
    start = time.time()
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FAILED: {result.stderr}")
        sys.exit(1)
    else:
        # Print only the last few lines to keep it clean
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines[-5:]:
            print(f"  > {line}")
        print(f"✅ Done in {time.time() - start:.2f}s")

def main():
    print("--- 🏭 STARTING GEMINI CODE REVERSE ENGINEERING PIPELINE ---")
    
    # 1. Update the Truth Map (Consolidates heuristic + grep findings)
    # We assume 'variable_map_final.json' is our source of truth now.
    
    # 2. Hydrate the Personas (Apply the map to the raw markdown)
    run_step("hydrate_personas.py", "Hydrating Personas with latest Map")
    
    # 3. Patch Tools (Ensure tool definitions match the map)
    run_step("patch_tools.py", "Patching Tool Definitions")
    
    # 4. Reconstruct Core Tools (Ensure Bash/Grep schemas are valid)
    run_step("reconstruct_core_tools.py", "Reconstructing Core Tool Schemas")
    
    # 5. Audit (The script we just wrote)
    run_step("audit_agent_logic.py", "Gemini Logic Audit")
    
    print("\n--- ✨ PIPELINE COMPLETE. READY FOR ENGINE START. ---")

if __name__ == "__main__":
    main()
