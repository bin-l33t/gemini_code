import sys
import re

def snipe(pattern, filepath, window=100):
    print(f"--- 🎯 Sniping '{pattern}' in {filepath} ---")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print("File not found.")
        return

    # Find all matches
    matches = [m for m in re.finditer(pattern, content)]
    print(f"Found {len(matches)} matches.")

    for i, m in enumerate(matches):
        if i >= 10: # Limit to 10 matches to avoid spam
            print("... (more matches hidden) ...")
            break
            
        start = max(0, m.start() - window)
        end = min(len(content), m.end() + window)
        
        snippet = content[start:end].replace('\n', ' ')
        print(f"\n[Match {i+1} @ {m.start()}]")
        print(f"...{snippet}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python snipe.py <regex_pattern> [filename]")
    else:
        target = sys.argv[1]
        file = sys.argv[2] if len(sys.argv) > 2 else "node_modules/@anthropic-ai/claude-code/cli.js"
        snipe(target, file)
