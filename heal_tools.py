import re
import json
import os
from google import genai
from google.genai import types

# Initialize Client
client = genai.Client(http_options={'api_version': 'v1alpha'})

# We will read the raw file again to get the broken snippets
CLI_PATH = "node_modules/@anthropic-ai/claude-code/cli.js"

print(f"--- 🚑 Healing Tool Schemas from {CLI_PATH} ---")

with open(CLI_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Regex to find things that look like inputSchema:{ ... }
# We capture a generous amount of text to let Gemini figure out the boundaries
matches = list(re.finditer(r'inputSchema:(\{.{10,1500}\})', content))

print(f"Found {len(matches)} raw schema candidates. Asking Gemini to fix them...")

cleaned_tools = []

for i, match in enumerate(matches):
    raw_snippet = match.group(1)
    
    # Skip if it's too short to be a real schema
    if len(raw_snippet) < 50:
        continue

    prompt = f"""
    You are a code de-obfuscator. I have a snippet of minified JavaScript that represents a JSON schema for a tool.
    It contains minified function calls like V9("string") or !0 (true).
    
    Your goal: Extract the schema and convert it to VALID, PURE JSON.
    - Convert !0 to true, !1 to false.
    - Convert function calls like V9("string") to just "string".
    - Convert property keys to double-quoted strings.
    - Remove any trailing code that isn't part of the schema object.
    - Return ONLY the JSON.

    Raw Snippet:
    {raw_snippet}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        fixed_json = json.loads(response.text)
        print(f"✅ [{i}] Healed schema.")
        cleaned_tools.append(fixed_json)
        
    except Exception as e:
        print(f"❌ [{i}] Failed to heal: {e}")

# Save the healed tools
with open("healed_tools.json", "w") as f:
    json.dump(cleaned_tools, f, indent=2)

print(f"--- Done. Saved {len(cleaned_tools)} valid tool definitions to healed_tools.json ---")
