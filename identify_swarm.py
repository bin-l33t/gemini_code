# Save as: identify_swarm.py
import os
from google import genai
from google.genai import types
import json

# Init Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def identify_persona(filename, content):
    prompt = f"""
    You are analyzing a system prompt extracted from a software engineering agent (Claude Code).
    
    FILENAME: {filename}
    CONTENT:
    {content[:3000]} # Truncated for speed
    
    TASK:
    1. Identify the specific ROLE of this agent (e.g. "Code Reviewer", "Test Runner", "Documentation Searcher", "Git Committer").
    2. Provide a snake_case name for the file (e.g. agent_code_reviewer.md).
    3. Provide a 1-sentence description.
    
    OUTPUT JSON ONLY:
    {{
        "role": "...",
        "filename": "...",
        "description": "..."
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

def main():
    print("--- 🕵️‍♀️ Identifying Swarm Personas ---")
    directory = "hydrated_personas"
    
    results = []
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Directory '{directory}' not found.")
        return

    for f in os.listdir(directory):
        if f.startswith("persona_") and f.endswith(".md"):
            path = os.path.join(directory, f)
            with open(path, "r") as file:
                content = file.read()
            
            try:
                info = identify_persona(f, content)
                
                # --- FIX START: Handle List vs Dict return ---
                if isinstance(info, list):
                    if len(info) > 0:
                        info = info[0]
                    else:
                        raise ValueError("Gemini returned an empty list.")
                # --- FIX END ---

                print(f"✅ {f} -> {info.get('filename', 'UNKNOWN')} ({info.get('role', 'UNKNOWN')})")
                
                if 'filename' in info:
                    # Renaissance: Rename the file
                    new_path = os.path.join(directory, info['filename'])
                    os.rename(path, new_path)
                    results.append(info)
                else:
                    print(f"⚠️  Skipping {f}: No filename in response.")

            except Exception as e:
                print(f"❌ Failed to identify {f}: {e}")

    with open("swarm_identity_map.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
