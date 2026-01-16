import re

def sniff_core_tools():
    print("--- 🕵️‍♀️ Sniffing for Core Tool Definitions ---")
    
    with open("node_modules/@anthropic-ai/claude-code/cli.js", "r") as f:
        content = f.read()

    # Look for the definition of the Bash tool specifically
    # We look for the string "Bash" followed closely by "description" or "tool"
    # Minified code often looks like: name:"Bash",description:"..."
    
    patterns = [
        r'name:"Bash".{0,100}',
        r'name:"Grep".{0,100}',
        r'name:"Glob".{0,100}',
        r'class LocalBashTask',
        r'function \w+\(A,Q\)\{return SD\(`grep' # Looking for the grep implementation wrapper
    ]

    for p in patterns:
        matches = re.findall(p, content)
        print(f"\nPattern: {p}")
        for m in matches[:3]:
            print(f"  FOUND: {m}")

    # Extract the 'safeFlags' object you saw in the grep output earlier
    # This defines what arguments are allowed in grep/ls
    print("\n--- 🕵️‍♀️ Extracting Allowed Flags ---")
    flag_match = re.search(r'safeFlags:(\{.*?\})', content)
    if flag_match:
        print(f"  safeFlags: {flag_match.group(1)[:200]}...")
    else:
        print("  safeFlags object not found.")

if __name__ == "__main__":
    sniff_core_tools()
