"""
verify_subagents.py
Surgically inspects 'subagent_type' and 'spawn' usage to identify hidden agents.
"""
import re
import json
import os
from google import genai
from google.genai import types

# Initialize Gemini
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

CLI_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"

def get_context(pattern, num_chars=1000):
    with open(CLI_FILE, "r") as f:
        content = f.read()
    
    matches = []
    for m in re.finditer(pattern, content):
        start = max(0, m.start() - num_chars // 2)
        end = min(len(content), m.end() + num_chars // 2)
        matches.append(content[start:end])
    return matches

def analyze_subagent_logic():
    print("--- 🕵️‍♀️ Investigating Subagent Architecture ---")
    
    # 1. Grab context around 'subagent_type'
    contexts = get_context(r"subagent_type", 800)
    if not contexts:
        print("❌ No 'subagent_type' found.")
        return

    prompt = f"""
    You are a reverse engineering expert. Analyze the following minified JavaScript snippets from `claude-code`.
    
    OBJECTIVE:
    1. Identify the tool variable name associated with "launches specialized agents". (Look for "The ${{VAR}} tool launches specialized agents").
    2. Identify the available `agentType` values (e.g., 'Bash', 'Plan').
    3. Determine if there are specific SYSTEM PROMPTS associated with these types.
    
    SNIPPETS:
    {json.dumps(contexts[:3], indent=2)}
    
    OUTPUT JSON FORMAT:
    {{
      "launch_tool_variable": "string (e.g., b3, AEA)",
      "agent_types": ["list", "of", "types"],
      "analysis": "Brief explanation of how subagents are spawned."
    }}
    """
    
    print("🧠 Asking Gemini to decode subagent logic...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    result = json.loads(response.text)
    print(json.dumps(result, indent=2))
    
    # 2. Verify specific subagents if found
    if "agent_types" in result:
        print(f"\n--- 🔬 verifying {len(result['agent_types'])} Subagents ---")
        for agent_type in result["agent_types"]:
            print(f"Searching for definition of agentType: '{agent_type}'...")
            # We look for where this agent type is DEFINED, usually near 'getSystemPrompt'
            type_context = get_context(f'agentType:"{agent_type}"', 600)
            if type_context:
                print(f"✅ Found definition for {agent_type}")
            else:
                print(f"⚠️  Definition not found for {agent_type}")

if __name__ == "__main__":
    analyze_subagent_logic()
