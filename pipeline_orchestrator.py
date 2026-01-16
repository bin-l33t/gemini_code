import os
import subprocess
import time
import argparse

def run_step(script_name, description, extra_args=None):
    print(f"\n🚀 --- STEP: {description} ({script_name}) ---")
    start = time.time()
    if not os.path.exists(script_name):
        print(f"❌ Error: Script {script_name} not found.")
        return False
    
    cmd = ["python3", script_name]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success ({time.time() - start:.2f}s)")
        # Print first few lines of output to show progress
        print("\n".join(result.stdout.split('\n')[:5]))
        return True
    else:
        print(f"🛑 FAILED")
        print(result.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Gemini Reverse Engineering Orchestrator")
    parser.add_argument("--limit", type=int, default=200, help="Mining limit for prompt extraction (Default: 200)")
    args = parser.parse_args()

    print(f"🤖 GEMINI REVERSE ENGINEERING ORCHESTRATOR 🤖 (Limit: {args.limit})")
    
    # 1. Verification of Environment
    if not run_step("test_genai.py", "Verifying Gemini API Access"): exit(1)

    # 2. Extract Raw Prompts (CRITICAL: Creates 'extracted_personas' dir)
    # We pass the limit argument here
    if not run_step("mine_prompts.py", "Mining System Prompts from CLI", extra_args=["--limit", str(args.limit)]): exit(1)

    # 3. Hunt for Variables (The 'Smart Hunt' logic)
    if not run_step("smart_hunt.py", "Hunting for Variable Definitions"): exit(1)
    
    # 4. Merge results into the master map
    if not run_step("merge_hunt_results.py", "Merging Hunt Results"): exit(1)

    # 5. Sanitize Map (Manual overrides for known issues)
    if not run_step("sanitize_map.py", "Sanitizing Variable Map"): exit(1)

    # 6. Hydrate Personas (Apply the map to the raw text)
    if not run_step("hydrate_personas_v2.py", "Hydrating Personas"): exit(1)

    # 7. Extract Tools (Get the JSON schemas)
    if not run_step("extract_schemas_full.py", "Extracting Tool Schemas"): exit(1)
    
    # 8. Merge Tools (Combine Core + Web tools)
    if not run_step("merge_tools.py", "Merging Tool Definitions"): exit(1)

    # 9. Gemini Audit (The Critical Step)
    if not run_step("verify_logic_with_gemini.py", "Auditing with Gemini API"): exit(1)

    print("\n✨ PIPELINE COMPLETE ✨")

if __name__ == "__main__":
    main()
