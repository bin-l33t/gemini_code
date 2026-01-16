import os
import re
import json
import shutil

# --- CONFIGURATION ---
SOURCE_DIR = "extracted_personas"
OUTPUT_DIR = "gemini_code_personas"
CORE_TOOLS_FILE = "core_tools_reconstructed.json"
WEB_TOOLS_FILE = "healed_tools.json"
FINAL_TOOLS_FILE = "master_tool_definitions.json"

# --- 1. THE GOLDEN MAP (Derived from your deep analysis) ---
# This dictionary represents the "Truth" extracted from your logs.
VARIABLE_MAP = {
    # Core Tool Names (Minified -> Real)
    "K9": "Bash",
    "BI": "Grep",
    "gI": "Glob",
    "C3": "Read",       # Was initially mapped to Bash/Read ambiguity, confirmed Read
    "f3": "Edit",
    "eZ": "Write",
    "Tq": "NotebookEdit",
    "mW.name": "TodoWrite",
    "b3": "Notebook",
    
    # Planner Variables (The ones causing failures)
    "A.planFilePath": "PLAN.md",
    "M$.name": "update_plan",
    "A$.name": "Edit",          # Context: "incremental edits"
    "Q$.name": "Edit",          # Context: "create your plan"
    "$Y": "Ask",                # Context: "yield control back"
    "mS.agentType": "Planner",
    
    # Documentation & Web Variables
    "mI": "WebFetch",
    "BR": "WebSearch",
    "nF5": "https://code.claude.com/docs/en/claude_code_docs_map.md",
    "DI2": "https://platform.claude.com/llms.txt",
    "aF5": "claude",
    "JI2": "Bash",
    
    # Common Minified Variables
    "A": "input_path",
    "Q": "options",
    "EE": "StructuredOutput",
    "W": "FileSystem", 
    "B": "Pattern"
}

def clean_output_dir():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"✅ Cleaned output directory: {OUTPUT_DIR}")

def merge_tools():
    """Merges Core Tools (Grep, etc) with Web Tools (Browser) into one definition file."""
    master_tools = []
    
    # Load Core
    if os.path.exists(CORE_TOOLS_FILE):
        with open(CORE_TOOLS_FILE, 'r') as f:
            core = json.load(f)
            # Ensure proper structure
            if isinstance(core, list):
                 master_tools.extend(core)
            print(f"✅ Loaded {len(core)} Core Tools")
    else:
        print(f"⚠️ Warning: {CORE_TOOLS_FILE} not found.")

    # Load Web
    if os.path.exists(WEB_TOOLS_FILE):
        with open(WEB_TOOLS_FILE, 'r') as f:
            web = json.load(f)
            # Web tools might be lists of lists due to previous extraction
            if isinstance(web, list):
                for item in web:
                    if isinstance(item, list):
                        master_tools.extend(item)
                    else:
                        master_tools.append(item)
            print(f"✅ Loaded {len(master_tools) - len(core) if 'core' in locals() else len(master_tools)} Web Tools")

    # Deduplicate by name
    unique_tools = {}
    for tool in master_tools:
        # Normalize tool definition
        if "function" in tool: # OpenAI format
            name = tool["function"]["name"]
            unique_tools[name] = tool
        elif "name" in tool: # Anthropic format
            name = tool["name"]
            # Convert to OpenAI format for consistent usage if needed, or keep as is
            # For this pipeline, we keep the raw structure but ensure unique names
            unique_tools[name] = tool
            
    final_list = list(unique_tools.values())
    
    with open(FINAL_TOOLS_FILE, 'w') as f:
        json.dump(final_list, f, indent=2)
    
    print(f"🎉 Saved {len(final_list)} unique tools to {FINAL_TOOLS_FILE}")
    return final_list

def smart_hydrate(text):
    """
    Hydrates variables handling both ${VAR} and ${VAR.prop}.
    Sorting keys by length (descending) is CRITICAL to prevent partial replacements.
    """
    sorted_keys = sorted(VARIABLE_MAP.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        val = VARIABLE_MAP[key]
        # Regex to match ${KEY} strictly
        # Escaping key because it might contain dots (e.g. A.planFilePath)
        escaped_key = re.escape(key)
        pattern = r"\$\{" + escaped_key + r"\}"
        
        # Replace
        text = re.sub(pattern, val, text)
        
    return text

def process_personas():
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Source directory {SOURCE_DIR} not found.")
        return

    processed_count = 0
    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".md"):
            continue
            
        src_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        hydrated_content = smart_hydrate(content)
        
        # Extra Cleanup: Remove leftover specific artifacts if any
        hydrated_content = hydrated_content.replace("${A.name}", "Bash") # Fallback
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(hydrated_content)
            
        processed_count += 1
        print(f"💧 Hydrated {filename}")

    print(f"✅ Processed {processed_count} personas.")

def main():
    print("--- 🚀 Starting Gemini Code Pipeline ---")
    clean_output_dir()
    tools = merge_tools()
    process_personas()
    print("--- Pipeline Complete. Artifacts ready in ./gemini_code_personas/ ---")

if __name__ == "__main__":
    main()
