import os
import re

# Directory containing the extracted personas
PERSONA_DIR = "extracted_personas"
SYSTEM_PROMPT = "extracted_system_prompt.txt"

# Keywords that likely signal a tool definition
KEYWORDS = [
    "tool definitions", 
    "available tools", 
    "you have access to", 
    "execute_bash", 
    "file_read", 
    "grep", 
    "function_call"
]

def scan_file(filepath):
    """Scans a single file for keywords and returns matching lines with context."""
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            for kw in KEYWORDS:
                if kw.lower() in line.lower():
                    # Grab 2 lines before and 4 lines after for context
                    start = max(0, i - 2)
                    end = min(len(lines), i + 5)
                    context = "".join(lines[start:end]).strip()
                    matches.append(f"\n[Line {i+1}] MATCH: '{kw}'\n{'-'*40}\n{context}\n{'-'*40}")
                    break # Move to next line if match found
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return matches

def main():
    print(f"--- 🔍 Scanning for Tool Definitions in {PERSONA_DIR} ---")
    
    # 1. Scan the main system prompt if it exists
    if os.path.exists(SYSTEM_PROMPT):
        print(f"\n📄 Scanning {SYSTEM_PROMPT}...")
        results = scan_file(SYSTEM_PROMPT)
        if results:
            print(f"✅ Found {len(results)} potential definitions!")
            for r in results: print(r)
        else:
            print("❌ No obvious tool definitions found.")

    # 2. Scan all personas
    files = sorted([f for f in os.listdir(PERSONA_DIR) if f.endswith(".md")])
    
    for filename in files:
        filepath = os.path.join(PERSONA_DIR, filename)
        results = scan_file(filepath)
        
        if results:
            print(f"\n📂 File: {filename}")
            # limit output to first 2 matches per file to avoid spamming
            for r in results[:2]: 
                print(r)
            if len(results) > 2:
                print(f"... and {len(results)-2} more matches.")

if __name__ == "__main__":
    main()
