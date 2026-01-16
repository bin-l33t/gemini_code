import os
import random
from google import genai
from google.genai import types

# Setup
client = genai.Client(http_options={'api_version': 'v1alpha'})
MODEL = "gemini-2.0-flash"
HYDRATED_DIR = "hydrated_personas"

def audit_file(filename):
    path = os.path.join(HYDRATED_DIR, filename)
    with open(path, "r") as f:
        content = f.read()

    # We take a sizable chunk to check context
    snippet = content[:2000]

    prompt = f"""
    I am reverse engineering an AI system prompt from minified code. 
    I have replaced variables like ${{A}} with tool names like "Bash" or "Edit".
    
    Please analyze the following text snippet. 
    1. Does it read like coherent English instructions?
    2. Are there any remaining obfuscated variables (like ${{X}}, ${{Q}}, etc)?
    3. Do the tool references (Bash, Edit, etc.) fit the context grammatically?
    
    TEXT SNIPPET:
    ---
    {snippet}
    ---
    
    Respond with: "STATUS: PASS" or "STATUS: FAIL" followed by a brief reason.
    """

    print(f"--- 🕵️‍♀️ Auditing {filename} ---")
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    print(response.text)
    print("-" * 30)

def main():
    files = [f for f in os.listdir(HYDRATED_DIR) if f.endswith(".md")]
    if not files:
        print("No hydrated files found.")
        return

    # Audit 3 random files
    samples = random.sample(files, min(3, len(files)))
    for s in samples:
        audit_file(s)

if __name__ == "__main__":
    main()
