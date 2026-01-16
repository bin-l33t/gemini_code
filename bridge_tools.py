import json
import os
from google.genai import types

def convert_json_schema_to_gemini(json_tool_list):
    """
    Converts a list of JSON tool definitions (OpenAI/Anthropic style)
    into google.genai.types.Tool objects.
    """
    funcs = []
    
    for tool in json_tool_list:
        if isinstance(tool, list): 
            for sub_tool in tool:
                funcs.append(_parse_single_tool(sub_tool))
        else:
            funcs.append(_parse_single_tool(tool))
            
    funcs = [f for f in funcs if f is not None]
    return types.Tool(function_declarations=funcs)

def _build_schema(schema_dict):
    """Recursively builds a google.genai.types.Schema object."""
    if not schema_dict:
        return None
        
    # 1. Handle Type Normalization
    raw_type = schema_dict.get("type", "OBJECT")
    
    # Handle multi-types (e.g. ["string", "number"]) -> Default to STRING for API simplicity
    if isinstance(raw_type, list):
        gemini_type = "STRING" 
    else:
        gemini_type = raw_type.upper()

    # 2. Base Schema Object
    schema = types.Schema(
        type=gemini_type,
        description=schema_dict.get("description", "")
    )

    # 3. Handle Objects (Properties)
    if gemini_type == "OBJECT" and "properties" in schema_dict:
        properties = {}
        required = schema_dict.get("required", [])
        
        for prop_name, prop_data in schema_dict["properties"].items():
            properties[prop_name] = _build_schema(prop_data)
            
        schema.properties = properties
        schema.required = required

    # 4. Handle Arrays (Items)
    if gemini_type == "ARRAY" and "items" in schema_dict:
        # Recursively build the schema for the items
        schema.items = _build_schema(schema_dict["items"])

    # 5. Handle Enums
    if "enum" in schema_dict:
        schema.enum = schema_dict["enum"]

    return schema

def _parse_single_tool(tool_dict):
    try:
        # Normalize name/desc/inputSchema
        name = tool_dict.get("name")
        description = tool_dict.get("description", "")
        input_schema = tool_dict.get("inputSchema") or tool_dict.get("parameters")

        # Fallback for nested function structure
        if not name and "function" in tool_dict:
            name = tool_dict["function"].get("name")
            description = tool_dict["function"].get("description")
            input_schema = tool_dict["function"].get("parameters")

        if not name:
            return None

        # Build the Function Declaration
        return types.FunctionDeclaration(
            name=name,
            description=description,
            parameters=_build_schema(input_schema)
        )
    except Exception as e:
        print(f"⚠️ Failed to convert tool {tool_dict.get('name', 'unknown')}: {e}")
        return None

def load_all_tools():
    all_tools_raw = []
    
    # Load Core Tools
    if os.path.exists("core_tools_reconstructed.json"):
        with open("core_tools_reconstructed.json") as f:
            all_tools_raw.extend(json.load(f))
            
    # Load Browser/Extra Tools
    if os.path.exists("healed_tools.json"):
        with open("healed_tools.json") as f:
            all_tools_raw.extend(json.load(f))
            
    return convert_json_schema_to_gemini(all_tools_raw)
