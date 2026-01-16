import json
from google.genai import types

def load_and_adapt_tools(filename="healed_tools.json"):
    """
    Loads raw JSON tools and wraps them in the correct Gemini SDK types.
    """
    with open(filename, "r") as f:
        raw_tools = json.load(f)

    # Flatten list of lists if necessary (some extraction scripts output [[tool1, tool2], [tool3]])
    flat_tools = []
    if isinstance(raw_tools, list):
        for item in raw_tools:
            if isinstance(item, list):
                flat_tools.extend(item)
            else:
                flat_tools.append(item)
    
    # Filter out "unknown_tool" or empty schemas
    valid_tools = [
        t for t in flat_tools 
        if t.get("name") and t.get("name") != "unknown_tool"
    ]

    # Convert to Gemini FunctionDeclaration format
    # Note: Google GenAI SDK uses specific Pydantic models, but often accepts dicts 
    # IF nested correctly under 'function_declarations'.
    
    # We wrap ALL functions into a SINGLE Tool object for the model
    return [types.Tool(function_declarations=valid_tools)]

if __name__ == "__main__":
    t = load_and_adapt_tools()
    print(f"✅ Adapted {len(t[0].function_declarations)} tools for Gemini.")
