"""
run_re_pipeline_v2.py
Improved Master Orchestrator: Streams output and checks for existing artifacts.
"""
import subprocess
import time
import sys
import os

# Definition of the pipeline steps
STEPS = [
    # 1. Extraction Phase
    # (CMD, DESC, CHECK_DIR)
    ("python3 mine_prompts.py", "⛏️  Mining System Prompts", "extracted_personas"),
    ("python3 deep_scan.py", "🔍 Scanning Variables", None),
    ("python3 dragnet.py", "🕸️  Dragging Net for Tool Names", None),
    
    # 2. Heuristic Phase
    ("python3 find_tools.py", "🛠️  Finding Tool Definitions", None),
    ("python3 heal_tools.py", "🚑 Healing JSON Schemas", "healed_tools.json"),
    ("python3 extract_core_tools.py", "🧬 Extracting Core Tools", None),
    ("python3 reconstruct_core_tools.py", "🧠 Reconstructing Core Logic", "core_tools_reconstructed.json"),
    
    # 3. Mapping Phase
    ("python3 smart_hunt.py", "🕵️‍♀️ Smart Hunting Variable Names", "smart_map.json"),
    ("python3 merge_hunt_results.py", "🔄 Merging Hunt Results", None),
    ("python3 sanitize_map.py", "🧹 Sanitizing Variable Map", "variable_map_sanitized.json"),
    ("python3 update_map_truth.py", "🔒 Locking Verified Mappings", None),
    ("python3 fix_planner_map.py", "🩹 Applying Planner Fixes", None),
    ("python3 fix_code_writer.py", "🩹 Applying Code Writer Fixes", None),
    
    # 4. Hydration Phase
    ("python3 hydrate_personas_v2.py", "💧 Hydrating Personas (Final)", "gemini_code_personas"),
    ("python3 identify_swarm.py", "🐝 Identifying Swarm Agents", "swarm_identity_map.json"),
    
    # 5. Verification Phase
    ("python3 gemini_audit_suite.py", "🧐 Running Gemini Audit Suite", "gemini_audit_final_report.json")
]

def run_step(command, description, artifact_check=None):
    print(f"\n--------------------------------------------------")
    print(f"👉 {description}")
    
    # SKIP CHECK: If artifact exists, ask user (or skip if obvious)
    if artifact_check and os.path.exists(artifact_check):
        # specific check for extracted_personas to avoid long API costs
        if "extracted_personas" in artifact_check:
             num_files = len(os.listdir(artifact_check))
             if num_files > 5:
                 print(f"   ⚠️  Found {num_files} existing personas in {artifact_check}.")
                 print(f"   ⏭️  SKIPPING {description} to save time/cost.")
                 return

    start_time = time.time()
    
    # Use Popen to stream output directly to the console (stdout=sys.stdout)
    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=sys.stdout, 
            stderr=sys.stderr
        )
        exit_code = process.wait()
        
        elapsed = time.time() - start_time
        
        if exit_code != 0:
            print(f"❌ FAILED: {description} (Exit Code: {exit_code})")
            # We don't exit hard here, allowing user to debug specific steps if needed
            # But usually, a failure here is critical.
            user_input = input("   Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                sys.exit(exit_code)
        else:
            print(f"✅ COMPLETED ({elapsed:.1f}s)")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Pipeline interrupted by user.")
        sys.exit(1)

def main():
    print("🚀 STARTING GEMINI CODE REVERSE ENGINEERING PIPELINE (V2)")
    print("==========================================================")
    
    for cmd, desc, check in STEPS:
        run_step(cmd, desc, check)
        
    print("\n🎉 PIPELINE COMPLETE. Artifacts ready in ./gemini_code_personas/")

if __name__ == "__main__":
    main()
