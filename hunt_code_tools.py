import re

# Read the minified file
with open("node_modules/@anthropic-ai/claude-code/cli.js", "r") as f:
    content = f.read()

print("--- 🕵️‍♀️ Hunting for Code Tool Definitions ---")

# We suspect variables like ${gI} (grep) or ${BI} (ls) are defined near their names.
# Let's search for where "grep" is assigned to a property.

# Search 1: Look for explicit name: "grep"
# Matches: name:"grep",description:"..."
patterns = [
    r'name:"grep",description:"(.*?)"',
    r'name:"ls",description:"(.*?)"',
    r'name:"edit",description:"(.*?)"',
    r'name:"bash",description:"(.*?)"'
]

found = False
for p in patterns:
    matches = re.finditer(p, content)
    for m in matches:
        found = True
        print(f"✅ Found Signature: {m.group(0)[:100]}...")

if not found:
    print("❌ Standard definition not found. Switching to variable assignment search...")
    # Search 2: Look for the variable definitions found in your deep scan
    # persona_765.md used ${gI} for grep. Let's find what gI is.
    # Pattern: gI={...} or gI=function
    
    # We are looking for something like: var gI={name:"grep"...}
    # But minified it might be: gI={name:"grep"...}
    
    grep_var_match = re.search(r'([a-zA-Z0-9_]+)=\{name:"grep"', content)
    if grep_var_match:
        print(f"✅ 'grep' is assigned to variable: {grep_var_match.group(1)}")
        
    ls_var_match = re.search(r'([a-zA-Z0-9_]+)=\{name:"ls"', content)
    if ls_var_match:
        print(f"✅ 'ls' is assigned to variable: {ls_var_match.group(1)}")

print("\n--- 🧠 Analysis ---")
print("If the above failed, the tools might be defined in the 'System Prompt' string itself")
print("rather than as separate JSON objects. Checking extracted prompts...")

# Check if the tool definitions are actually INSIDE the hydrated prompts
import os
files = os.listdir("hydrated_personas")
for file in files:
    with open(f"hydrated_personas/{file}", "r") as f:
        fc = f.read()
        if "name: grep" in fc or "name: \"grep\"" in fc:
             print(f"✅ Found 'grep' definition inside prompt file: {file}")
