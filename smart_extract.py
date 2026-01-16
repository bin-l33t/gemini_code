import re
import sys

def smart_extract(file_path):
    print(f"--- 1. Reading {file_path} ---")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Regex to find anything inside backticks `...` (Template Literals)
    # or double quotes "..." that are very long.
    print("--- 2. Scanning for string literals... ---")
    
    # We look for backtick strings specifically as that's where multi-line prompts live
    candidates = re.findall(r'`([^`]{500,})`', content)
    
    print(f"--- 3. Found {len(candidates)} long candidates. Filtering for Natural Language... ---")

    valid_prompts = []
    
    for i, s in enumerate(candidates):
        # HEURISTIC 1: Whitespace Ratio
        # Normal English text is ~15-20% spaces. Minified code is <3%.
        space_count = s.count(' ')
        ratio = space_count / len(s)
        
        # HEURISTIC 2: Key Phrases
        # We know it's a prompt if it talks to the AI.
        markers = ["You are", "Agent", "Anthropic", "Claude", "context", "user"]
        has_marker = any(m in s for m in markers)

        # strict filter: Must look like English (ratio > 0.10) AND have a marker
        if ratio > 0.10 and has_marker:
            valid_prompts.append((ratio, s))

    print(f"--- 4. Success! Found {len(valid_prompts)} likely system prompts. ---")
    
    # Sort by length (longest is usually the main prompt)
    valid_prompts.sort(key=lambda x: len(x[1]), reverse=True)

    for idx, (ratio, prompt) in enumerate(valid_prompts):
        print(f"\n[{idx+1}] Confidence: {ratio:.2f} | Length: {len(prompt)}")
        print("Preview: " + prompt[:200].replace('\n', ' ') + "...")
        print("-" * 60)
        
        # Save the top result to a clean file
        if idx == 0:
            with open('extracted_system_prompt.txt', 'w') as out:
                out.write(prompt)
            print(">> SAVED TOP CANDIDATE TO 'extracted_system_prompt.txt'")

if __name__ == "__main__":
    # Point this to your actual file location
    path = "node_modules/@anthropic-ai/claude-code/cli.js" 
    smart_extract(path)
