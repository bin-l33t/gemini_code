import os
import sys
import subprocess

STEPS = [
    ("1. Sanitizing Map", "sanitize_map.py"),
    ("2. Re-Hydrating Personas", "hydrate_personas_v2.py"), # We will use the sanitized map here
    ("3. Merging Tools", "merge_tools_final.py"),
    ("4. Final Audit", "audit_master_v2.py")
]

def run_step(name, script):
    print(f"\n>>> 🚀 RUNNING: {name} ({script})")
    if not os.path.exists(script):
        print(f"❌ Script not found: {script}")
        return False
        
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FAILED:\n{result.stderr}")
        return False
    else:
        print(f"✅ SUCCESS:\n{result.stdout[-500:]}") # Print last 500 chars
        return True

if __name__ == "__main__":
    for name, script in STEPS:
        if not run_step(name, script):
            print("🛑 Pipeline stopped due to error.")
            break
    print("\n🎉 Pipeline Complete.")
