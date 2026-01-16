import re

TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def snipe(keyword, context=100):
    print(f"\n--- 🎯 Sniping: '{keyword}' ---")
    with open(TARGET_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Find all occurrences
    matches = [m.start() for m in re.finditer(re.escape(keyword), content)]
    
    if not matches:
        print("❌ No matches found.")
        return

    print(f"Found {len(matches)} matches. Showing first 3 contexts:")
    
    for i, start_idx in enumerate(matches[:3]):
        # Extract context window
        start_ctx = max(0, start_idx - context)
        end_ctx = min(len(content), start_idx + len(keyword) + context)
        snippet = content[start_ctx:end_ctx]
        
        # Clean up newlines for display
        snippet = snippet.replace("\n", " ")
        
        print(f"\n[Match {i+1}]: ...{snippet}...")

# We are looking for where the tools are defined in the JS object
# They usually look like: name:"Bash" or name:"Edit"
snipe('name:"Bash"') 
snipe('name:"Edit"')
snipe('name:"Grep"')
snipe('name:"Glob"')
