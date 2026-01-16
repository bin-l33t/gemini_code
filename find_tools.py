# Save as find_tools.py
import re

path = "node_modules/@anthropic-ai/claude-code/cli.js"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Look for standard tool definition patterns
print("--- 🛠️  Hunting for Tool Definitions ---")
patterns = [
    r'name:"grep",description:".*?"',
    r'name:"ls",description:".*?"',
    r'inputSchema:\{.*?\}',
    r'json_schema:\{.*?\}'
]

for p in patterns:
    matches = re.findall(p, content, re.DOTALL)
    print(f"Pattern '{p}': Found {len(matches)} matches.")
    for m in matches[:3]: # Show first 3
        print(f"  Found: {m[:100]}...")
