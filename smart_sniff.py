# smart_sniff.py
import re
import sys

TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def sniff(pattern, context=100):
    print(f"--- 👃 Sniffing for '{pattern}' ---")
    try:
        with open(TARGET_FILE, 'r', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: cli.js not found.")
        return

    # Find all matches
    regex = re.compile(pattern)
    matches = list(regex.finditer(content))
    
    print(f"found {len(matches)} matches.")
    
    for i, m in enumerate(matches[:5]): # Limit to top 5
        start = max(0, m.start() - context)
        end = min(len(content), m.end() + context)
        snippet = content[start:end].replace('\n', ' ')
        
        print(f"\n[Match {i+1} @ {m.start()}]")
        # Highlight match in output
        print(f"...{snippet}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_sniff.py <regex_pattern>")
        sys.exit(1)
    
    sniff(sys.argv[1])
