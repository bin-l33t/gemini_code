import re

FILE_PATH = "node_modules/@anthropic-ai/claude-code/cli.js"

def scan_file(): print("--- 🕵️‍♀️ Surgical Tool Audit ---") try: with open(FILE_PATH, 'r', encoding='utf-8') as f: content = f.read() except FileNotFoundError: print("❌ cli.js not found.") return

# 1. Search for File Writing Logic
# We look for fs.writeFileSync or similar patterns associated with variables
print("\n[1] Checking Write Implementation:")
write_patterns = [
    r'.{0,50}writeFileSync\(.{0,50}',
    r'.{0,50}fs\.write.{0,50}',
    r'.{0,50}applyPatch.{0,50}',  # Looking for patching logic
]

for p in write_patterns:
    matches = re.findall(p, content)
    for m in matches[:5]: # Limit to top 5
        print(f"  Found: ...{m}...")

# 2. Search for 'Edit' tool definition in the raw text
# We are looking for the "Edit" string near "inputSchema"
print("\n[2] Checking 'Edit' Tool Schema Context:")
# Look for the word "Edit" followed closely by inputSchema properties
schema_pattern = r'name:"Edit".{0,100}inputSchema:.{0,200}'
matches = re.findall(schema_pattern, content)
if matches:
    for m in matches:
        print(f"  Found Schema: {m}")
else:
    print("  ⚠️ No explicit 'Edit' schema found near name definition.")

# 3. Check for the RipGrep execution (The 'Grep' tool)
print("\n[3] Checking Grep/RipGrep Construction:")
grep_patterns = [
    r'.{0,50}rg".{0,50}',
    r'.{0,50}spawn\("rg".{0,50}'
]
for p in grep_patterns:
    matches = re.findall(p, content)
    for m in matches[:5]:
        print(f"  Found: ...{m}...")
scan_file() 
