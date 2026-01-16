import re

SOURCE_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
# The variables we saw in your prompts that need resolution
TARGETS = ["mW", "b3", "EE", "C3", "K9", "BI", "gI", "eZ"]

def find_definitions():
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {SOURCE_FILE}")
        return

    print(f"--- Hunting for definitions of: {', '.join(TARGETS)} ---")

    for var in TARGETS:
        print(f"\n🔎 Analyzing {var}...")
        
        # Pattern: [boundary] var = { ... }
        # We look for the variable followed by an equals sign and an object bracket
        # Using string concatenation to avoid f-string syntax errors
        pattern_str = r'(?:^|[, \t\n])' + re.escape(var) + r'\s*=\s*(\{.*?\})'
        
        match = re.search(pattern_str, content, re.DOTALL)
        
        if match:
            blob = match.group(1)
            # Try to find a "name" property inside
            name_match = re.search(r'name:"(.*?)"', blob)
            if name_match:
                print(f"   ✅ RESOLVED: {var} -> name: '{name_match.group(1)}'")
            else:
                print(f"   ⚠️  Found assignment, but no clear name: {blob[:100]}...")
        else:
            print(f"   ❌ Definition not found")

if __name__ == "__main__":
    find_definitions()
