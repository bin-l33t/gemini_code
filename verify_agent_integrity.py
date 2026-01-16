# verify_agent_integrity.py
import os
import json
import glob
from google import genai
from google.genai import types

# 1. Setup
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load your artifacts
tools_def = load_json("master_tool_definitions.json")
personas = glob.glob("hydrated_personas/*.md")

print(f"--- 🕵️‍♀️ GEMINI AGENT INTEGRITY AUDIT ---")
print(f"Loaded {len(tools_def)} tool definitions.")

for persona_path in personas:
    if "planner" not in persona_path and "engineer" not in persona_path:
        continue # Focus on the main agents for now

    print(f"\n🔎 Auditing: {persona_path}...")
    system_prompt = load_file(persona_path)
    
    # 2. Construct the Audit Prompt
    audit_prompt = f"""
    You are a Senior AI Systems Engineer. Your job is to audit an "Agent Persona" against a set of "Available Tools".
    
    CONTEXT:
    We have reverse-engineered a system prompt (Persona) and a set of tool definitions (Tools) from a minified codebase.
    We need to verify if the Persona is "coherent" -- meaning it only asks to use tools that actually exist, and uses them correctly.

    INPUTS:
    
    [[SYSTEM PROMPT / PERSONA]]
    {system_prompt[:15000]} # Truncate if too huge
    
    [[AVAILABLE TOOLS JSON]]
    {json.dumps(tools_def, indent=2)}

    TASK:
    1. **Variable Check**: Are there any obfuscated variables left in the System Prompt (e.g., ${{A.something}})?
    2. **Tool Hallucination Check**: Does the System Prompt mention tools that are NOT in the Available Tools JSON? (e.g. prompt says "Use Bash" but JSON only has "RunCommand")
    3. **Schema Alignment**: The prompt might say "Use the 'Bash' tool with 'command' argument". Does the JSON schema support this?
    4. **Executability Score**: Rate 0-100 on how ready this agent is to run.
    
    OUTPUT FORMAT:
    JSON with keys: status (PASS/FAIL), score (0-100), issues (list of strings), missing_tools (list).
    """

    # 3. Call Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=audit_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    # 4. Report
    result = json.loads(response.text)
    print(f"   SCORE: {result['score']}/100")
    print(f"   STATUS: {result['status']}")
    if result['issues']:
        print("   🚩 ISSUES:")
        for issue in result['issues']:
            print(f"      - {issue}")
