import re
import os
import json

# Path to the CLI file we are reverse engineering
CLI_PATH = "./node_modules/@anthropic-ai/claude-code/cli.js"

def scan_for_variables():
    """
    Scans the minified CLI code for template literal variables 
    (e.g., ${EE}, ${mW.name}) to help us understand what they map to.
    """
    if not os.path.exists(CLI_PATH):
        print(f"❌ Error: Could not find {CLI_PATH}")
        return

    print(f"--- 🔍 Deep Scanning {CLI_PATH} ---")
    
    with open(CLI_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Regex to find ${...} patterns
    # We look for short variable names often used in minified code
    pattern = r"\$\{([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*)\}"
    matches = re.findall(pattern, content)
    
    # Count frequency to find the most common ones
    from collections import Counter
    counts = Counter(matches)
    
    print(f"✅ Found {len(counts)} unique variable patterns.")
    print("\n--- Top 10 Most Frequent Variables ---")
    for var, count in counts.most_common(10):
        print(f"  ${{{var}}}: {count} occurrences")

    # Context Sniffer: Try to find what these variables definition might look like
    # We look for assignments like var EE = "exit_tool"
    print("\n--- 🕵️‍♀️ Context Sniffer (Best Guesses) ---")
    
    # Common tools usually found in this context
    suspects = {
        "EE": ["exit", "done", "submit"],
        "mW": ["tool", "agent", "task"],
        "DJ1": ["bash", "cmd"]
    }

    for var, likely_meanings in suspects.items():
        if var in counts:
            # Try to find the definition in minified code (heuristic)
            # Look for "const EE=" or "var EE=" or "EE:"
            regex_def = r"([a-zA-Z0-9_]+)\s*[:=]\s*['\"]([a-zA-Z0-9_]+)['\"]"
            definitions = re.findall(regex_def, content)
            
            candidates = [val for key, val in definitions if key == var]
            if candidates:
                print(f"  Possible value for ${{{var}}}: {candidates}")
            else:
                print(f"  Could not auto-decode ${{{var}}}, likely complex object.")

    # Also scan the extracted personas to see which files use which variables
    print("\n--- 📂 Variable Usage in Personas ---")
    persona_dir = "extracted_personas"
    if os.path.exists(persona_dir):
        for filename in os.listdir(persona_dir):
            if filename.endswith(".md"):
                with open(os.path.join(persona_dir, filename), 'r') as f:
                    p_content = f.read()
                    file_vars = set(re.findall(pattern, p_content))
                    if file_vars:
                        print(f"  {filename}: {', '.join(['${'+v+'}' for v in file_vars])}")

if __name__ == "__main__":
    scan_for_variables()
