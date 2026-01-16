import re

# Save as locate_execution.py
path = "node_modules/@anthropic-ai/claude-code/cli.js"
print(f"--- 🔍 Surgical Scan of {path} ---")

try:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 1. Check for Tool Execution logic (How arguments are passed)
    # We look for "Bash" or "Edit" inside quotes, likely followed by argument handling
    targets = [
        '"Bash"', 
        '"Edit"', 
        '"Grep"', 
        'fs.writeFile',  # How Edit likely works
        'child_process.spawn', # How Bash likely works
        'spawn('
    ]

    for target in targets:
        print(f"\n🎯 Target: {target}")
        matches = [m.start() for m in re.finditer(re.escape(target), content)]
        print(f"   Found {len(matches)} occurrences.")
        
        # Show the first 5 meaningful contexts
        count = 0
        for start in matches:
            if count >= 5: break
            
            # Extract window
            s = max(0, start - 100)
            e = min(len(content), start + 150)
            snippet = content[s:e].replace('\n', ' ')
            
            # Filter out some noise (optional)
            print(f"   [{s}-{e}] ...{snippet}...")
            count += 1

except FileNotFoundError:
    print("❌ cli.js not found. Make sure you are in the gemini_code directory.")
