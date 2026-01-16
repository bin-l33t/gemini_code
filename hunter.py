import re

FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def hunt():
    try:
        with open(FILE, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        print("❌ Error: cli.js not found.")
        return
    
    # 1. Resolve 'nu' (The name of the Planner tool)
    print("--- 🕵️‍♀️ Resolving 'mW' (Planner) Name ---")
    # We look for: nu="something"
    nu_match = re.search(r'\bnu\s*=\s*["\'](.*?)["\']', data)
    if nu_match:
        print(f"✅ RESOLVED: mW.name (nu) = '{nu_match.group(1)}'")
    else:
        print("❌ Could not resolve 'nu' directly.")

    # 2. Hunt for 'grep' (To find where system tools are hiding)
    print("\n--- 🛠️  Hunting for 'grep' Tool Definition ---")
    # Find where "grep" appears as a string literal. 
    # This will show us the structure of the missing tools.
    indices = [m.start() for m in re.finditer(r'["\']grep["\']', data)]
    for i in indices[:3]: # First 3 matches are enough
        start = max(0, i - 100)
        end = min(len(data), i + 200)
        print(f"\nCONTEXT (Index {i}):")
        # Print a snippet of code around "grep"
        print(f"...{data[start:end]}...")

    # 3. Hunt for 'EE' (The Exit/Result Tool)
    print("\n--- 🚪 Hunting for 'EE' (Exit Tool) ---")
    # Look for usage like EE(res) or EE({ ... })
    ee_matches = [m.start() for m in re.finditer(r'\bEE\(', data)]
    if not ee_matches:
        # Try finding definition: function EE(
        ee_matches = [m.start() for m in re.finditer(r'function\s+EE\s*\(', data)]
    
    for i in ee_matches[:3]:
        start = max(0, i - 50)
        end = min(len(data), i + 150)
        print(f"\nCONTEXT (Index {i}):")
        print(f"...{data[start:end]}...")

if __name__ == "__main__":
    hunt()
