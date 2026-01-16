# Save as audit_hydration.py
import os
import re

def audit():
    print("--- 🧐 Auditing Hydrated Personas for Artifacts ---")
    
    personas_dir = "hydrated_personas"
    issues_found = 0
    
    # Regex to find unhydrated variables like ${A}, ${mW.name}
    variable_pattern = re.compile(r"\$\{[a-zA-Z0-9_.]+\}")
    
    for filename in os.listdir(personas_dir):
        if not filename.endswith(".md"): continue
        
        path = os.path.join(personas_dir, filename)
        with open(path, "r") as f:
            content = f.read()
            
        matches = variable_pattern.findall(content)
        
        # Filter out legit template literals if they look like code, 
        # but warn about suspicious ones.
        suspicious = [m for m in matches if m not in ["${HOME}", "${PATH}"]]
        
        if suspicious:
            issues_found += 1
            print(f"⚠️  {filename}: Found {len(suspicious)} unhydrated variables.")
            print(f"    Examples: {suspicious[:3]}")
    
    if issues_found == 0:
        print("✅ CLEAN. No unhydrated variables found in personas.")
    else:
        print(f"❌ ISSUES. {issues_found} personas still contain raw variables.")

if __name__ == "__main__":
    audit()
