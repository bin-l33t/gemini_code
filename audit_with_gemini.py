import os
import glob
from google import genai
from google.genai import types

# Initialize Client
client = genai.Client(http_options={'api_version': 'v1alpha'})

def audit_persona(filename):
    with open(filename, "r") as f:
        content = f.read()

    print(f"--- 🕵️‍♀️ Auditing {os.path.basename(filename)} ---")
    
    prompt = f"""
    You are a Code Forensic Analyst. I have reverse-engineered a system prompt from a minified Javascript application. 
    I have attempted to "hydrate" (de-obfuscate) the variable names, but some may remain.
    
    Analyze the following System Prompt. 
    1. Identify any remaining obfuscated variables (look for patterns like ${{X}}, ${{Ab}}, or nonsensical variable names).
    2. Rate the "Coherence" from 0-10. Does the prompt make logical sense as an AI agent instruction?
    3. List any tools mentioned that seem undefined.
    
    SYSTEM PROMPT:
    {content[:10000]} # Limit to first 10k chars to fit context if needed
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    
    print(response.text)
    print("\n" + "="*30 + "\n")

# Run on the problematic file first, then others
target_files = ["hydrated_personas/persona_765.md", "hydrated_personas/agent_engineer.md"] 
# Add logic to scan all if needed, but start small to save tokens
for text_file in target_files:
    if os.path.exists(text_file):
        audit_persona(text_file)
