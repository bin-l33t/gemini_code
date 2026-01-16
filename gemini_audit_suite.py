import os
import json
import time
from google import genai
from google.genai import types

# --- CONFIG ---
PERSONAS_DIR = "gemini_code_personas"
TOOLS_FILE = "master_tool_definitions.json"
CRITICAL_FILES = ["agent_planner.md", "persona_765.md", "agent_engineer.md"]

def get_client():
    # Checked GEMINI_API_KEY first as requested
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Fallback just in case
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment.")
        return None
    return genai.Client(api_key=api_key)

def load_tools():
    if not os.path.exists(TOOLS_FILE):
        return []
    with open(TOOLS_FILE, 'r') as f:
        return json.load(f)

def audit_file(client, filename, tools_json):
    filepath = os.path.join(PERSONAS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"⚠️ File {filename} not found, skipping.")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    # Create a concise tool list string for the prompt
    tool_names = []
    for tool in tools_json:
        if "name" in tool:
            tool_names.append(tool["name"])
        elif "function" in tool:
            tool_names.append(tool["function"]["name"])
    
    tools_str = ", ".join(tool_names)

    prompt = f"""
    You are a Senior Compiler and Logic Analyzer for AI Agents.
    
    I will provide you with:
    1. A list of AVAILABLE TOOLS.
    2. A SYSTEM PROMPT for an AI Agent.
    
    Your Job:
    Verify if the SYSTEM PROMPT is executable.
    
    Check for:
    1. **Obfuscated Variables**: Are there any remaining syntaxes like ${{A.something}} or ${{K9}}?
    2. **Tool Hallucinations**: Does the prompt instruct the agent to use a tool that is NOT in the AVAILABLE TOOLS list? (e.g. if it says "Use Grep" but Grep is not in the list).
    3. **Logic Gaps**: Are there instructions that are impossible to follow?
    
    ---
    AVAILABLE TOOLS: {tools_str}
    ---
    SYSTEM PROMPT ({filename}):
    {content}
    ---
    
    Respond in JSON format:
    {{
        "filename": "{filename}",
        "score": (0-100 integer),
        "status": "PASS" or "FAIL",
        "remaining_variables": ["list", "of", "found", "vars"],
        "missing_tools": ["list", "of", "missing", "tools"],
        "critique": "Short explanation."
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error auditing {filename}: {e}")
        return None

def main():
    print("--- 🕵️‍♀️ Starting Gemini Critical Audit ---")
    client = get_client()
    if not client: return

    tools = load_tools()
    print(f"Loaded {len(tools)} tools definition for context.")

    results = []
    
    # Audit specific critical files first, then the rest if needed
    files_to_audit = CRITICAL_FILES
    
    for filename in files_to_audit:
        print(f"Auditing {filename}...")
        result = audit_file(client, filename, tools)
        if result:
            results.append(result)
            print(f"   Score: {result['score']} - {result['status']}")
            if result['status'] == 'FAIL':
                print(f"   Missing: {result['missing_tools']}")
                print(f"   Vars: {result['remaining_variables']}")
        time.sleep(1) # Rate limit politeness

    # Save Report
    with open("gemini_audit_final_report.json", 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✅ Audit Complete. Results in gemini_audit_final_report.json")

if __name__ == "__main__":
    main()
