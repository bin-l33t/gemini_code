import re

FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def dragnet():
    try:
        with open(FILE, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        print("❌ Error: cli.js not found.")
        return

    print("--- 🕸️  Dragging the Net for Tool Names ---")
    
    # 1. Find all "name" properties in objects
    # Pattern: name:"value" or name:'value'
    name_matches = re.findall(r'name\s*:\s*["\'](.*?)["\']', data)
    
    # Filter for tool-like names (no spaces, usually lowercase or CamelCase)
    # We exclude common JS property names like 'id', 'class', etc. to reduce noise.
    candidates = set()
    for name in name_matches:
        if len(name) > 2 and len(name) < 20 and " " not in name:
            candidates.add(name)
            
    print(f"✅ Found {len(candidates)} unique 'name' candidates.")
    print("\nPossible Tools (Top Candidates):")
    # Print sorted list to spot "Bash", "Edit", "Write", etc.
    for c in sorted(list(candidates)):
        print(f"  - {c}")

    print("\n--- 🕵️‍♀️ Brute Force 'EE' Search ---")
    # Search for any string assignment to EE
    # EE = "something" or EE = 'something'
    ee_assign = re.search(r'\bEE\s*=\s*["\'](.*?)["\']', data)
    if ee_assign:
        print(f"✅ RESOLVED: EE = '{ee_assign.group(1)}'")
    else:
        # Check if EE is an object property
        ee_prop = re.search(r'\bEE\s*:\s*["\'](.*?)["\']', data)
        if ee_prop:
             print(f"✅ RESOLVED: EE (property) = '{ee_prop.group(1)}'")
        else:
            print("❌ EE assignment still not found. It might be passed as an argument.")

if __name__ == "__main__":
    dragnet()
