"""
run_re_pipeline.py
Master Orchestrator for the Gemini Code Reverse Engineering Pipeline.
"""
import subprocess
import time
import sys
import os

STEPS = [
    # 1. Extraction Phase
    ("python3 mine_prompts.py", "⛏️  Mining System Prompts"),
    ("python3 deep_scan.py", "🔍 Scanning Variables"),
    ("python3 dragnet.py", "🕸️  Dragging Net for Tool Names"),
    
    # 2. Heuristic Phase
    ("python3 find_tools.py", "🛠️  Finding Tool Definitions"),
    ("python3 heal_tools.py", "🚑 Healing JSON Schemas"),
    ("python3 extract_core_tools.py", "🧬 Extracting Core Tools"),
    ("python3 reconstruct_core_tools.py", "🧠 Reconstructing Core Logic"),
    
    # 3. Mapping Phase
    ("python3 smart_hunt.py", "🕵️‍♀️ Smart Hunting Variable Names"),
    ("python3 merge_hunt_results.py", "🔄 Merging Hunt Results"),
    ("python3 sanitize_map.py", "🧹 Sanitizing Variable Map"),
    ("python3 update_map_truth.py", "🔒 Locking Verified Mappings"),
    ("python3 fix_planner_map.py", "🩹 Applying Planner Fixes"),
    ("python3 fix_code_writer.py", "🩹 Applying Code Writer Fixes"),
    
    # 4. Hydration Phase
    ("python3 hydrate_personas_v2.py", "💧 Hydrating Personas (Final)"),
    ("python3 identify_swarm.py", "🐝 Identifying Swarm Agents"),
    
    # 5. Verification Phase
    ("python3 gemini_audit_suite.py", "🧐 Running Gemini Audit Suite")
]

def run_step(command, description):
    print(f"\n>>> {description}...")
    start_time = time.time()
    try:
        # Capture output to avoid cluttering, only show on error
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        elapsed = time.time() - start_time
        print(f"✅ Done ({elapsed:.1f}s)")
        # Print specific success metrics if useful (optional)
        if "Audit" in description:
            print(result.stdout) 
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR in step: {description}")
        print(e.stderr)
        print(e.stdout)
        sys.exit(1)

def main():
    print("🚀 STARTING GEMINI CODE REVERSE ENGINEERING PIPELINE")
    print("====================================================")
    
    for cmd, desc in STEPS:
        run_step(cmd, desc)
        
    print("\n🎉 PIPELINE COMPLETE. Artifacts ready in ./hydrated_personas/ and ./gemini_code_personas/")

if __name__ == "__main__":
    main()
