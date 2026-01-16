import re
import json

SOURCE_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def extract_schemas():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find inputSchema defined in the JS objects
    # This looks for inputSchema:{ ... } patterns
    pattern = re.compile(r'inputSchema:(\{.*?\})(?:,|$)', re.DOTALL)
    
    matches = pattern.findall(content)
    print(f"--- Found {len(matches)} potential tool schemas ---")

    cleaned_schemas = []
    
    for i, match in enumerate(matches):
        # The JS objects aren't valid JSON (keys aren't quoted), we need to try to clean them minimally
        # or just print them for manual inspection if they are complex.
        print(f"\n[Schema {i+1}]")
        # Print first 300 chars to identify the tool
        print(match[:500] + "..." if len(match) > 500 else match)

if __name__ == "__main__":
    extract_schemas()
