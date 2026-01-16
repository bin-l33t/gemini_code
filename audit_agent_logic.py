# audit_agent_logic.py
import os
import glob
from google import genai
from google.genai import types

client = genai.Client(http_options={'api_version': 'v1alpha'})

def audit_persona(filename):
    with open(filename, "r") as f:
        content = f.read()

    # We ask Gemini to be a Code Auditor
    prompt = f"""
    You are a Static Analysis Tool for AI Agent Prompts.
    Analyze the following System Prompt for a "Gemini Code" agent.
    
    FILE: {filename}
    
    CHECKLIST:
    1. Are there any obfuscated variables left (e.g., ${{A}}, ${{X}}, ${{nF5}})?
    2. Does the prompt mention tools (Bash, Edit, Glob) that look correctly named?
    3. Is the logic coherent? (e.g. Does it tell the user to "read a file" without saying how?)
    
    SYSTEM PROMPT CONTENT:
    {content[:15000]} # Truncate if massive, though most are <5k
    
    OUTPUT FORMAT:
    STATUS: [PASS/FAIL]
    ISSUES: [List specific obfuscated vars or logic errors]
    CONFIDENCE: [High/Medium/Low]
    """

    print(f"--- 🕵️‍♀️ Auditing {os.path.basename(filename)} ---")
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0
        )
    )
    
    print(response.text)
    print("-" * 30)

# Run on key agents first
files = sorted(glob.glob("extracted_personas/agent_*.md")) + sorted(glob.glob("extracted_personas/persona_765.md"))

for file in files:
    audit_persona(file)
