import re
import os

# Define the signatures of the agents we identified from your previous output
# We use unique substrings to find them in the file reliably.
AGENT_SIGNATURES = {
    "agent_architect.md": "You are an elite AI agent architect specializing in crafting",
    "agent_guide.md": "You are the Claude guide agent. Your primary responsibility is",
    "agent_planner.md": "You are a software architect and planning specialist for Claude Code",
    "agent_search.md": "You are a file search specialist for Claude Code",
    "agent_engineer.md": "You are an interactive CLI tool that helps users with software engineering tasks",
    "agent_commit.md": "Only create commits when requested by the user. If unclear, ask first",
    "agent_summary.md": "Your task is to create a detailed summary of the conversation so far",
}

def extract_personas(file_path):
    print(f"--- Reading {file_path} ---")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    # Create output directory
    os.makedirs("gemini_code_personas", exist_ok=True)
    
    found_count = 0
    
    # We use the same regex to get the chunks (strings inside backticks > 500 chars)
    # This matches the strategy that worked in smart_extract.py
    candidates = re.findall(r'`([^`]{500,})`', content)
    
    print(f"--- Scanning {len(candidates)} chunks for known Agent Personas ---")

    for filename, signature in AGENT_SIGNATURES.items():
        found = False
        for chunk in candidates:
            if signature in chunk:
                # Clean up: Replace escaped newlines if necessary
                # JS minification often leaves \n as literal characters
                clean_chunk = chunk.replace('\\n', '\n').replace('\\"', '"')
                
                with open(f"gemini_code_personas/{filename}", "w") as out:
                    out.write(clean_chunk)
                
                print(f"✅ Extracted: {filename} ({len(clean_chunk)} chars)")
                found = True
                found_count += 1
                break
        
        if not found:
            print(f"❌ Could not find signature for: {filename}")

    print(f"\n--- Extraction Complete. Found {found_count}/{len(AGENT_SIGNATURES)} Agents ---")
    print("Files are located in: gemini_code_personas/")

if __name__ == "__main__":
    # Point this to your actual file location
    path = "node_modules/@anthropic-ai/claude-code/cli.js" 
    extract_personas(path)
