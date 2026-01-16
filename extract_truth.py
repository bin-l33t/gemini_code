import re

# File path
CLI_PATH = "node_modules/@anthropic-ai/claude-code/cli.js"

def extract_variable_definitions():
    with open(CLI_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # The minified code often uses patterns like: var K9="Bash";var gI="Glob"
    # We look for: var (2-3 chars) = "(ToolName)"
    pattern = re.compile(r'var\s+([a-zA-Z0-9]{2,3})="(Bash|Grep|Glob|View|Edit|Read|Write|LS|Todo|Notebook)"')
    
    matches = pattern.findall(content)
    
    print(f"--- 🕵️‍♀️ FOUND {len(matches)} DEFINITIVE DEFINITIONS ---")
    print(f"{'VAR':<10} | {'TRUE VALUE'}")
    print("-" * 30)
    
    mapping = {}
    for var_name, tool_name in matches:
        print(f"${{{var_name}}}".ljust(10) + f" | {tool_name}")
        mapping[f"${{{var_name}}}"] = tool_name
        
    return mapping

if __name__ == "__main__":
    extract_variable_definitions()
