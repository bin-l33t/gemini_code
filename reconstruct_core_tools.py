# Save as reconstruct_core_tools.py
import json
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def reconstruct_tools():
    # Load a heavy-hitter persona that uses core tools
    with open("hydrated_personas/agent_engineer.md", "r") as f:
        engineer_prompt = f.read()

    print("--- 🧠 Reconstructing Core Tools from Agent Prompts ---")
    print("Asking Gemini to infer tool schemas based on how the Agent Engineer is told to use them...")

    prompt = f"""
    Below is the System Prompt for an autonomous coding agent. 
    It contains instructions on how to use specific tools (likely named Bash, Grep, Glob, View, Edit, etc.).
    
    Based ONLY on the instructions in this prompt, generate a valid JSON Tool Definition (function declaration) for the following tools:
    1. Bash (executing commands)
    2. Grep (searching files)
    3. View (reading files)
    4. Edit (modifying files)
    5. Glob (listing files)
    
    Output ONLY the JSON list of tool definitions.
    
    SYSTEM PROMPT:
    {engineer_prompt[:10000]} # First 10k chars should contain the tool instructions
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    tools = json.loads(response.text)
    
    # Save them
    with open("core_tools_reconstructed.json", "w") as f:
        json.dump(tools, f, indent=2)
    
    print(f"✅ Reconstructed {len(tools)} core tools. Saved to core_tools_reconstructed.json")

if __name__ == "__main__":
    reconstruct_tools()
