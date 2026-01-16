import json
import os
import sys
from google import genai
from google.genai import types

# Configuration
AGENT_FILE = "hydrated_personas/agent_engineer.md"
TOOLS_FILE = "master_tool_definitions.json"
MODEL_ID = "gemini-2.0-flash"

def load_text(path):
    if not os.path.exists(path):
        print(f"❌ CRITICAL: Missing file {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_json(path):
    if not os.path.exists(path):
        print(f"❌ CRITICAL: Missing file {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sanitize_tools(raw_tools):
    """Converts extracted tool definitions to Gemini SDK format."""
    sanitized = []
    for tool in raw_tools:
        # Handle cases where tool might be wrapped in "function" key or not
        fn_data = tool.get("function", tool)
        
        props = fn_data.get("parameters", {}).get("properties", {})
        reqs = fn_data.get("parameters", {}).get("required", [])
        
        # Ensure required params exist in properties
        valid_reqs = [r for r in reqs if r in props]

        tool_decl = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name=fn_data.get("name"),
                    description=fn_data.get("description"),
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            k: types.Schema(
                                type=v.get("type", "STRING").upper(),
                                description=v.get("description", "")
                            ) for k, v in props.items()
                        },
                        required=valid_reqs
                    )
                )
            ]
        )
        sanitized.append(tool_decl)
    return sanitized

def run_test():
    print("🤖 STARTING AUTOMATED AGENT TEST")
    
    # 1. Load Persona
    system_instruction = load_text(AGENT_FILE)
    print(f"✅ Loaded Persona: {AGENT_FILE} ({len(system_instruction)} chars)")

    # 2. Load and Sanitize Tools
    raw_tools = load_json(TOOLS_FILE)
    gemini_tools = sanitize_tools(raw_tools)
    print(f"✅ Loaded & Sanitized {len(gemini_tools)} tools")

    # 3. Initialize Client
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: No API Key found.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)

    # 4. Execute "Hello World" Prompt
    print("\n🧪 Sending Prompt: 'Write a Hello World python script to hello.py'")
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                tools=gemini_tools,
                system_instruction=system_instruction,
                temperature=0.1 # Low temp for deterministic testing
            ),
            contents="Write a Hello World python script to hello.py. Explain how to run it."
        )

        # 5. Validation Logic
        print("\n--- RESPONSE ANALYSIS ---")
        
        # We expect either a Tool Call (Write/Edit) OR code blocks in text
        has_code = False
        has_tool = False
        
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    print(f"🛠️  Agent called tool: {part.function_call.name}")
                    print(f"    Args: {part.function_call.args}")
                    has_tool = True
                if part.text:
                    print(f"📝 Agent text: {part.text[:100]}...")
                    if "print(\"Hello, World!\")" in part.text or 'print("Hello, World!")' in part.text:
                        has_code = True

        if has_tool or has_code:
            print("\n✅ TEST PASSED: Agent behaved intelligently.")
            sys.exit(0)
        else:
            print("\n❌ TEST FAILED: Agent did not produce code or tool calls.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ RUNTIME ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
