import os
import json
from google import genai
from google.genai import types

# Initialize Client
try:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("❌ Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

def verify_persona(filename, tool_defs):
    with open(filename, "r") as f:
        content = f.read()

    print(f"🕵️‍♀️ Auditing {os.path.basename(filename)}...")

    prompt = f"""
    You are a Code Logic Auditor. I will provide you with a 'System Prompt' extracted from a reverse-engineered CLI tool, and a list of 'Available Tools' (JSON).
    
    Your Job:
    1. Check for **Obfuscated Variables**: Are there any remaining strings like ${{A}}, ${{nF5}}, or ${{M$.name}}?
    2. Check for **Phantom Tools**: Does the prompt tell the user to use a tool (e.g. "Use the TodoList tool") that does NOT exist in the Available Tools list?
    3. Check for **Logic Gaps**: Are there instructions that are impossible to follow?

    SYSTEM PROMPT:
    {content}

    AVAILABLE TOOLS (JSON):
    {json.dumps(tool_defs, indent=2)}

    Return a JSON object with this structure:
    {{
        "filename": "{os.path.basename(filename)}",
        "status": "PASS" or "FAIL",
        "obfuscated_variables": ["list", "of", "vars"],
        "missing_tools": ["list", "of", "tools"],
        "logic_critique": "A brief summary of issues."
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
        return {"status": "ERROR", "error": str(e)}

def main():
    # Load Tools
    if os.path.exists("master_tool_definitions.json"):
        with open("master_tool_definitions.json", "r") as f:
            tools = json.load(f)
    else:
        print("⚠️ master_tool_definitions.json not found. Assuming empty tool list.")
        tools = []

    report = []
    
    # Scan hydrated personas
    persona_dir = "hydrated_personas"
    if not os.path.exists(persona_dir):
        print(f"❌ Error: Directory {persona_dir} not found.")
        return

    # Prioritize the Agent Planner for this test
    files = ["agent_planner.md"] + [f for f in os.listdir(persona_dir) if f != "agent_planner.md" and f.endswith(".md")]
    
    for f in files[:3]: # limit to top 3 for speed
        filepath = os.path.join(persona_dir, f)
        if os.path.exists(filepath):
            result = verify_persona(filepath, tools)
            report.append(result)
            
            # Print immediate feedback
            status_icon = "✅" if result.get("status") == "PASS" else "❌"
            print(f"   {status_icon} {result.get('filename')}: {result.get('status')}")
            if result.get("status") == "FAIL":
                print(f"      Missing Vars: {result.get('obfuscated_variables')}")
                print(f"      Missing Tools: {result.get('missing_tools')}")

    # Save Report
    with open("gemini_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n📄 Full audit report saved to gemini_audit_report.json")

if __name__ == "__main__":
    main()
