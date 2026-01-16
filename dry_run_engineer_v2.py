import os
import json
from google import genai
from google.genai import types

# Load the inferred tools
with open("core_tools_reconstructed.json", "r") as f:
    raw_tools = json.load(f)

# Load the hydrated system prompt
with open("hydrated_personas/agent_engineer.md", "r") as f:
    system_instruction = f.read()

# --- THE FIX: Convert OpenAI JSON to Gemini FunctionDeclaration ---
def convert_to_gemini_tools(raw_tools):
    declarations = []
    for tool in raw_tools:
        # Handle the structure: {"type": "function", "function": {...}}
        if "function" in tool:
            fn_def = tool["function"]
        else:
            fn_def = tool # Handle flat structure if present
            
        # Extract schema properties
        properties = fn_def.get("parameters", {}).get("properties", {})
        required = fn_def.get("parameters", {}).get("required", [])
        
        declarations.append(
            types.FunctionDeclaration(
                name=fn_def["name"],
                description=fn_def["description"],
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        k: types.Schema(type="STRING", description=v.get("description", "")) 
                        for k, v in properties.items()
                    },
                    required=required
                )
            )
        )
    return [types.Tool(function_declarations=declarations)]

gemini_tools = convert_to_gemini_tools(raw_tools)
print(f"✅ Converted {len(gemini_tools[0].function_declarations)} tools to Gemini format.")

# Initialize Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

print("\n--- 🧪 Dry Run: Agent Engineer (Gemini 2.0 Flash) ---")
print("User: 'List the files in the current directory'")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=gemini_tools,
        temperature=0 # Keep it deterministic for testing
    ),
    contents=["List the files in the current directory"]
)

# Parse the response to see if it tries to call a tool
print("\nResponse:")
if response.function_calls:
    for fc in response.function_calls:
        print(f"🛠️  TOOL CALL: {fc.name}({fc.args})")
else:
    print(response.text)
