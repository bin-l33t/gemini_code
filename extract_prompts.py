import re
import json

SOURCE_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
OUTPUT_FILE = "claude_strings.json"

def extract_strings():
    print(f"--- Reading {SOURCE_FILE} (11MB) ---")
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ File not found. Check path.")
        return

    print("--- Extracting String Literals (This may take a moment) ---")
    # Regex to find double-quoted, single-quoted, and backtick strings
    # We focus on backticks (`) first as they often contain multiline prompts in JS
    
    # Pattern for backticks: `...`
    backtick_pattern = re.compile(r'`([^`]*)`')
    
    matches = backtick_pattern.findall(content)
    
    print(f"--- Found {len(matches)} string literals inside backticks ---")

    # Filter for "interesting" strings (likely prompts)
    # Heuristic: Prompts are usually long (> 100 chars) and contain spaces
    long_strings = [s for s in matches if len(s) > 200]
    
    print(f"--- Filtered down to {len(long_strings)} potential prompts (>200 chars) ---")
    
    # Sort by length (longest first) - The main system prompt is usually massive
    long_strings.sort(key=len, reverse=True)

    data = {
        "top_50_longest_strings": long_strings[:50]
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Extraction complete. Saved top candidates to '{OUTPUT_FILE}'.")
    
    # Preview the longest one
    if long_strings:
        print("\n🔎 PREVIEW OF LONGEST STRING (Likely the Main System Prompt):")
        print("-" * 60)
        print(long_strings[0][:500] + "...") 
        print("-" * 60)

if __name__ == "__main__":
    extract_strings()
