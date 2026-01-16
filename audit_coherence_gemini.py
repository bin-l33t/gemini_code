import os
import json
from google import genai
from google.genai import types

# --- CONFIG ---
API_KEY = os.environ.get("GOOGLE_API_KEY") # Ensure this is set
PERSONAS_DIR = "hydrated_personas"
TOOLS_FILE = "master_tool_definitions.json"

client = genai.Client(api_key=API_KEY)

def load_tools():
    if os.path.exists(TOOLS_FILE):
        with open(TOOLS_FILE, 'r') as f:
            return json.load(f)
    return []

def audit_persona(filename, content, tools_json):
    print(f"\n--- 🕵️‍♀️ Auditing {filename} with Gemini ---")
    
    prompt = f"""
    You are a Senior Software Architect specializing in reverse-engineering and code auditing.
    
    Analyze the following SYSTEM PROMPT for an AI Agent.
    I have also provided the LIST OF AVAILABLE TOOLS that this agent technically has access to.
    
    YOUR GOAL: Verify Coherence and Detect Hallucinations.
    
    --- AVAILABLE TOOLS (JSON) ---
    {json.dumps(tools_json, indent=2)}
    
    --- SYSTEM PROMPT TO AUDIT ---
    {content}
    
    --- INSTRUCTIONS ---
    1. Identify any "Obfuscated Variables" remaining (e.g., ${{A}}, ${{nF5}}).
    2. Check for "Phantom Tools": Does the prompt ask the agent to use a tool that is NOT in the Available Tools list? (e.g., "Use the Planner tool" when only "Bash" exists).
    3. Check for "Logic Gaps": Are there instructions that are impossible to follow given the tools?
    4. Rate the "Executability" on a scale of 0-100%.
    
    FORMAT OUTPUT AS JSON:
    {{
      "filename": "{filename}",
      "executability_score": 0,
      "obfuscated_vars": [],
      "phantom_tools": [],
      "logic_issues": [],
      "verdict": "PASS/FAIL"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Error auditing {filename}: {e}")
        return None

def main():
    tools = load_tools()
    results = []
    
    files = [f for f in os.listdir(PERSONAS_DIR) if f.endswith(".md")]
    
    # Audit top critical agents first
    priority_files = ["agent_engineer.md", "agent_planner.md", "agent_architect.md"]
    
    for fname in priority_files:
        if fname in files:
            with open(os.path.join(PERSONAS_DIR, fname), 'r') as f:
                content = f.read()
            
            audit = audit_persona(fname, content, tools)
            if audit:
                results.append(audit)
                print(json.dumps(audit, indent=2))

    # Save Report
    with open('final_audit_report.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
