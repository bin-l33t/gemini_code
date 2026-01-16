import os
import re

# 1. Define the Mapping (Derived from your crack_map.py and human logic)
# These are the variables Anthropic injects into the prompt at runtime.
VARIABLE_MAP = {
    r"\$\{A\}": "View",           # File Reader
    r"\$\{Q\}": "Edit",           # File Editor
    r"\$\{mW.name\}": "Planner",  # Task Management
    r"\$\{b3\}": "Notebook",      # Jupyter/Python exec
    r"\$\{C3\}": "Bash",          # Shell execution
    r"\$\{gI\}": "Grep",          # Search
    r"\$\{BI\}": "LS",            # List Files
    r"\$\{EE\}": "StructuredOutput", # Exit/Return
    r"\$\{K9\}": "Glob",          # File Pattern Matching
    # Sanitizing generic JS injections
    r"\$\{.*?\}": "TOOL_UNKNOWN" 
}

SOURCE_DIR = "extracted_personas"
DEST_DIR = "hydrated_personas"

def hydrate_file(filename):
    with open(os.path.join(SOURCE_DIR, filename), 'r') as f:
        content = f.read()
    
    # Apply replacements
    for pattern, replacement in VARIABLE_MAP.items():
        content = re.sub(pattern, replacement, content)
        
    # Write to new folder
    with open(os.path.join(DEST_DIR, filename), 'w') as f:
        f.write(content)
    print(f"✅ Hydrated: {filename}")

if __name__ == "__main__":
    os.makedirs(DEST_DIR, exist_ok=True)
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')]
    print(f"--- 💧 Hydrating {len(files)} Personas ---")
    for f in files:
        hydrate_file(f)
