import os
import glob
from google import genai
from google.genai import types

# Initialize
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def audit_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # We ask Gemini to simulate the agent and report setup errors
    prompt = f"""
    I am a developer debugging a system prompt for an AI agent. 
    Below is the raw markdown content of the prompt.
    
    TASK:
    1. Scan for any remaining obfuscated variables (e.g., ${{A}}, ${{nF5}}, ${{mW.name}}).
    2. Check if the tools mentioned (like 'Bash', 'Edit') are actually defined or if they are just vague references.
    3. Rate the "Executability" of this prompt from 0 to 10.
    4. If the score is below 10, list the specific variables that need to be fixed.

    --- SYSTEM PROMPT BEGIN ---
    {content}
    --- SYSTEM PROMPT END ---
    
    Output Format:
    STATUS: [PASS/FAIL]
    SCORE: [0-10]
    ISSUES: [List of specific extracted variables or logic gaps]
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    
    print(f"\n--- 🕵️‍♀️ Auditing {filepath} ---")
    print(response.text)
    return response.text

# Audit specific problematic files first
targets = [
    "hydrated_personas/agent_planner.md", 
    "hydrated_personas/persona_765.md",
    "hydrated_personas/agent_engineer.md"
]

for t in targets:
    if os.path.exists(t):
        audit_file(t)
