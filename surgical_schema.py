import re

CLI_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

# Coordinates found in your locate_execution.py logs
TARGETS = [
    {"name": "Bash_Def", "offset": 2346141, "var": "K9"},
    {"name": "Edit_Def", "offset": 2350474, "var": "f3"},
    {"name": "Grep_Def", "offset": 2347632, "var": "BI"},
    # Also looking for the View tool, usually near Edit
    {"name": "View_Search", "offset": 2350474, "var": "View"}, 
]

def analyze_context(text, center, window=1000):
    start = max(0, center - window)
    end = min(len(text), center + window)
    snippet = text[start:end]
    return snippet

print(f"--- 🏥 Surgical Extraction from {CLI_FILE} ---")

try:
    with open(CLI_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    for target in TARGETS:
        print(f"\n🔎 Examining {target['name']} around offset {target['offset']}...")
        snippet = analyze_context(content, target['offset'], window=800)
        
        # Save to file for inspection
        filename = f"trace_{target['name']}.txt"
        with open(filename, "w") as out:
            out.write(snippet)
        
        # Quick check for schema keywords
        if "properties" in snippet or "inputSchema" in snippet:
             print(f"   ✅ FOUND 'properties' or 'inputSchema' in {filename}")
        else:
             print(f"   ⚠️  Schema keywords not immediately visible. Check {filename} manually.")

        # Print a small preview to stdout (safe size)
        print(f"   📝 Preview: {snippet[750:900]}...")  # Center of the snippet

except FileNotFoundError:
    print("❌ Error: cli.js not found at expected path.")
