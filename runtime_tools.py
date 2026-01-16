import subprocess
import os

# Point to the binary you found in the logs
RG_PATH = os.path.abspath("node_modules/@anthropic-ai/claude-code/vendor/ripgrep/x64-linux/rg")

def grep_tool(pattern, path=".", case_insensitive=True):
    """
    Implements the 'grep' tool capability using the extracted ripgrep binary.
    """
    if not os.path.exists(RG_PATH):
        return f"Error: ripgrep binary not found at {RG_PATH}"

    cmd = [RG_PATH, "--line-number", "--no-heading"]
    if case_insensitive:
        cmd.append("-i")
    
    cmd.append(pattern)
    cmd.append(path)

    try:
        # Run the binary
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        
        if not output:
            return "No matches found."
            
        # Truncate if too long to avoid overflowing context window
        lines = output.split('\n')
        if len(lines) > 50:
            return "\n".join(lines[:50]) + f"\n... ({len(lines)-50} more matches truncated)"
        
        return output
    except Exception as e:
        return f"Grep failed: {str(e)}"

# Quick Test
if __name__ == "__main__":
    print("Testing grep tool on current directory...")
    # Search for "Gemini" in the python files
    print(grep_tool("Gemini", "*.py"))
