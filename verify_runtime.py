import os
import re
import sys
from google import genai
from google.genai import types

def extract_system_prompt(file_path):
    """Extracts the 'Clean Text' block from the persona markdown."""
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r") as f:
        content = f.read()
    
    # Try to find content between ```markdown and ``` markers
    match = re.search(r"```markdown\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        return match.group(1)
    
    # Fallback: Return the whole content if no code blocks found
    return content

def run_agent_test():
    print(f"--- 🚀 Initializing Gemini Hello System: AGENT_ENGINEER ---")
    
    # 1. Load the Persona
    persona_path = "hydrated_personas/agent_engineer.md"
    system_instruction = extract_system_prompt(persona_path)
    
    if not system_instruction:
        print(f"❌ Error: Could not load persona from {persona_path}")
        return False

    print(f"✅ Loaded hydrated persona: {persona_path} ({len(system_instruction)} chars)")

    # 2. Initialize Client
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: API Key not found.")
        return False
        
    client = genai.Client(api_key=api_key)

    # 3. Execute Test
    user_prompt = "Write a simple 'Hello World' script in Python. Explain how to run it."
    print(f"--- 🧪 Executing Hello World Test ---")
    print(f"USER >>> {user_prompt}\n")

    try:
        # Generate with the Agent's persona as system instruction
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7 
            )
        )
        
        print(f"[AGENT_ENGINEER]: {response.text}\n")
        
        # Simple Validation
        if "print" in response.text and "Hello" in response.text:
            print("--------------------------------------------------")
            print("✅ TEST PASSED: Agent successfully generated code.")
            return True
        else:
            print("⚠️ TEST WARNING: Output did not match expected 'Hello World' pattern.")
            return False

    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        return False

if __name__ == "__main__":
    success = run_agent_test()
    # Early stopping: Exit with error code if test fails
    sys.exit(0 if success else 1)
