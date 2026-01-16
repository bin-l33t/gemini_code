"""
run_re_pipeline_v3.py
Master Orchestrator V3: Adds control flags (--force, --clean) and real-time logging.
"""
import subprocess
import time
import sys
import os
import shutil
import argparse

# Definition of the pipeline steps
# Format: (COMMAND, DESCRIPTION, ARTIFACT_DIR_OR_FILE)
STEPS = [
    # 1. Extraction Phase
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

def clean_artifacts():
    """Deletes artifact directories to ensure a fresh run."""
    dirs_to_clean = ["extracted_personas", "gemini_code_personas", "hydrated_personas"]
    files_to_clean = ["smart_map.json", "variable_map_sanitized.json", "variable_map_final.json"]
    
    print("\n🧹 CLEANING ARTIFACTS...")
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"   Deleted directory: {d}")
            except Exception as e:
                print(f"   ❌ Failed to delete {d}: {e}")
    
    for f in files_to_clean:
        if os.path.exists(f):
            os.remove(f)
            print(f"   Deleted file: {f}")

def run_step(command, description, artifact_check, force_mode):
    print(f"\n--------------------------------------------------")
    print(f"👉 {description}")
    
    # CHECK: Should we skip?
    if artifact_check and not force_mode and os.path.exists(artifact_check):
        # Specific logic for directories (check if empty)
        if os.path.isdir(artifact_check):
            if len(os.listdir(artifact_check)) > 5:
                print(f"   ⚠️  Artifacts exist in '{artifact_check}'.")
                print(f"   ⏭️  SKIPPING (Use --force to override).")
                return
        # Logic for files
        else:
            print(f"   ⚠️  Artifact '{artifact_check}' exists.")
            print(f"   ⏭️  SKIPPING (Use --force to override).")
            return

    start_time = time.time()
    
    # Stream output to console
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
            user_input = input("   Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                sys.exit(exit_code)
        else:
            print(f"✅ COMPLETED ({elapsed:.1f}s)")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Pipeline interrupted by user.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Gemini Code Reverse Engineering Pipeline")
    parser.add_argument("--force", action="store_true", help="Run all steps even if artifacts exist (overwrites data).")
    parser.add_argument("--clean", action="store_true", help="Delete all artifact directories before starting.")
    args = parser.parse_args()

    print("🚀 STARTING GEMINI CODE PIPELINE (V3)")
    print(f"   Mode: {'FORCE' if args.force else 'Standard'}")
    if args.clean:
        clean_artifacts()

    print("=====================================")
    
    for cmd, desc, check in STEPS:
        run_step(cmd, desc, check, args.force)
        
    print("\n🎉 PIPELINE COMPLETE. Artifacts ready in ./gemini_code_personas/")

if __name__ == "__main__":
    main()
