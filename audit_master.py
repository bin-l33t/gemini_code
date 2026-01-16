import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def audit_persona(persona_path, tools_path="healed_tools.json"):
    with open(persona_path, "r") as f:
        prompt_text = f.read()
    
    with open(tools_path, "r") as f:
        tools_json = f.read()

    audit_prompt = f"""
    You are a Senior Software Architect auditing a reverse-engineered AI Agent.
    
    ### COMPONENT 1: SYSTEM PROMPT (Draft)
    {prompt_text[:15000]} ... (truncated if too long)

    ### COMPONENT 2: AVAILABLE TOOLS (JSON)
    {tools_json}

    ### YOUR TASK
    Critically analyze the coherence between the System Prompt and the Tools.
    1. **Variable Check**: Are there any remaining obfuscated variables (like ${{A}}, ${{K9}})?
    2. **Tool Alignment**: The prompt instructs the agent to use specific tools (e.g., "Use Bash", "Use Edit"). Do these tools exist in the JSON?
    3. **Logic Check**: Are there instructions that are impossible to execute given the tools? (e.g., "Read the file" but no Read tool exists).

    ### OUTPUT FORMAT (JSON ONLY)
    {{
        "status": "PASS" or "FAIL",
        "coherence_score": (1-10),
        "obfuscated_variables": ["list", "of", "vars"],
        "missing_tools": ["tools", "mentioned", "but", "missing"],
        "critical_issues": ["description of logical fallacies"]
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=audit_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    return json.loads(response.text)

print("--- 🕵️‍♀️ Starting Master Audit ---")
personas = ["hydrated_personas/agent_engineer.md", "hydrated_personas/agent_planner.md", "hydrated_personas/persona_765.md"]

for p in personas:
    print(f"\nAUDITING: {p}")
    try:
        result = audit_persona(p)
        print(json.dumps(result, indent=2))
        if result["status"] == "FAIL":
            print("❌ Audit Failed.")
    except Exception as e:
        print(f"Error auditing {p}: {e}")
