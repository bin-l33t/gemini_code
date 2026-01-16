import re

# Read the CLI file
with open('node_modules/@anthropic-ai/claude-code/cli.js', 'r') as f:
    content = f.read()

print("--- 🕵️‍♀️ Refuting/Verifying Variables based on Usage ---")

# Heuristic 1: Find FileSystem operations to identify Path and Encoding
# Pattern: readFileSync(VAR, VAR)
fs_pattern = re.search(r'readFileSync\(\s*([$a-zA-Z0-9]+)\s*,\s*([$a-zA-Z0-9]+)\s*\)', content)
if fs_pattern:
    path_var = fs_pattern.group(1)
    opts_var = fs_pattern.group(2)
    print(f"✅ DETECTED: {path_var} is likely 'FilePath'")
    print(f"✅ DETECTED: {opts_var} is likely 'Encoding/Options'")

# Heuristic 2: Find Directory operations
# Pattern: readdirSync(VAR)
dir_pattern = re.search(r'readdirSync\(\s*([$a-zA-Z0-9]+)\s*\)', content)
if dir_pattern:
    print(f"✅ DETECTED: {dir_pattern.group(1)} is passed to readdirSync")

# Heuristic 3: Find Execution operations (Bash)
# Look for exec or spawn
exec_pattern = re.search(r'execSync\(\s*([$a-zA-Z0-9]+)\s*', content)
if exec_pattern:
    print(f"✅ DETECTED: {exec_pattern.group(1)} is likely 'CommandString'")

print("\n--- Recommended Update to crack_map.py ---")
print("Update your dictionary with the variables found above.")
