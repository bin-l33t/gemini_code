import json
import os
from google import genai
from google.genai import types

# 1. Load the "Truth" Mappings to ensure we are sane
TRUTH_MAP = {
    "${K9}": "Bash",
    "${gI}": "Glob",
    "${BI}": "Grep",
    "${C3}": "Read", # This was the conflict point
    "${f3}": "Edit",
    "${eZ}": "Write"
}

print("--- 1. Verifying Persona Hydration ---")
# Check Agent Engineer for artifacts
with open("hydrated_personas/agent_engineer.md", "r") as f:
    content = f.read()
    
failed = False
for var, name in TRUTH_MAP.items():
    if var in content:
        print(f"❌ CRITICAL FAIL: Found raw variable {var} in agent_engineer.md. Hydration incomplete.")
        failed = True
    # specific check for the C3/Bash mixup
    if name == "Read" and "Read" not in content and "Bash" in content:
         # This is a heuristic check, just seeing if Read is mentioned where we expect it
         pass 

if not failed:
    print("✅ Personas appear cleanly hydrated.")
else:
    print("⚠️ Stopping. Please re-run 'python hydrate_personas.py' now that 'variable_map.json' is updated.")
    exit()

# 2. Fix Tool Schemas for Google GenAI SDK
print("\n--- 2. Sanitizing Tool Schemas ---")

# Load the reconstructed tools
with open("core_tools_reconstructed.json", "r") as f:
    raw_tools = json.load(f)

sanitized_tools = []

for tool in raw_tools:
    # Anthropic extraction usually gives us { "type": "function", "function": { ... } }
    # Google SDK often wants just the function declaration part for the list
    
    fn_data = tool.get("function", tool)
    
    # Clean up 'required' fields - ensure they match properties
    props = fn_data.get("parameters", {}).get("properties", {})
    reqs = fn_data.get("parameters", {}).get("required", [])
    
    # Filter required list to only include keys that actually exist in properties
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
    sanitized_tools.append(tool_decl)

print(f"✅ Sanitized {len(sanitized_tools)} tools for Gemini.")

# 3. The Live Test
print("\n--- 3. Testing with Gemini API ---")
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

sys_prompt = "You are a helpful assistant. Use the Bash tool to list files."

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            tools=sanitized_tools,
            system_instruction=sys_prompt,
            temperature=0
        ),
        contents="List the files in the current directory."
    )
    
    print("\nSTATUS: RESPONSE RECEIVED")
    # Check if tool call happened
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                print(f"✅ SUCCESS! Model called tool: {part.function_call.name}")
                print(f"   Args: {part.function_call.args}")
            else:
                print(f"Text response: {part.text}")
    else:
        print("⚠️ Response empty.")

except Exception as e:
    print(f"❌ API ERROR: {e}")
    print("This usually means the schema is still slightly off. Check 'sanitized_tools' construction.")
