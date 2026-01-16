import os
import re

# Save this as audit_variables.py
files = os.listdir("extracted_personas")
variable = "${A}"

print(f"--- Auditing usage of {variable} ---")
for f in files:
    with open(f"extracted_personas/{f}", "r") as file:
        content = file.read()
        if variable in content:
            # Get 50 chars of context around the variable
            matches = re.findall(r'.{0,50}\$\{A\}.{0,50}', content)
            print(f"\n📂 {f}:")
            for m in matches:
                print(f"  ...{m}...")
