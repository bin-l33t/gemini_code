import re
import sys
from google import genai
from google.genai import types

# Configure your API key here or in env
client = genai.Client(http_options={'api_version': 'v1alpha'})

PATTERN_VAR_DEF = re.compile(r'var\s+([a-zA-Z0-9_]+)\s*=\s*"([^"]+)"')
TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def get_context(content, start, end, window=100):
    s = max(0, start - window)
    e = min(len(content), end + window)
    return content[s:e]

print(f"--- 🕵️‍♀️ Smart Hunting in {TARGET_FILE} ---")

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Find all `var X = "String"` candidates
matches = list(PATTERN_VAR_DEF.finditer(content))
print(f"Found {len(matches)} variable definitions. Filtering for likely Tool/Agent names...")

candidates = []
for m in matches:
    var_name = m.group(1)
    val = m.group(2)
    
    # Heuristic: We only care about short vars (obfuscated) mapping to Capitalized words (Tools)
    # or known patterns like "Bash", "Grep", "Todo"
    if len(var_name) <= 3 and (val[0].isupper() or val in ["grep", "glob", "ls"]):
        candidates.append((var_name, val, m.start(), m.end()))

print(f"🔍 Found {len(candidates)} high-probability candidates.")

found_vars = {}

for var_name, val, start, end in candidates:
    ctx = get_context(content, start, end)
    print(f"\nChecking: {var_name} = '{val}'")
    
    # Use Gemini to verify if this looks like a tool definition context
    prompt = f"""
    I am reverse engineering minified JS. 
    Analyze this snippet:
    
    `...{ctx}...`
    
    Does the variable `{var_name}` appear to be an alias for a Tool Name, Agent Name, or Command?
    Return JSON: {{ "is_tool": boolean, "category": "tool" | "agent" | "other", "confidence": float }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        res_json = response.parsed
        if res_json and res_json['is_tool'] and res_json['confidence'] > 0.8:
            print(f"✅ CONFIRMED: ${{ {var_name} }} -> {val} ({res_json['category']})")
            found_vars[f"${{{var_name}}}"] = val
    except Exception as e:
        print(f"⚠️ API Error: {e}")

import json
print("\n--- 💾 Saving Verified Map to smart_map.json ---")
with open('smart_map.json', 'w') as f:
    json.dump(found_vars, f, indent=2)
