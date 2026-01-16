import os
import re
import json
from google import genai
from google.genai import types

# --- CONFIGURATION ---
TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
OUTPUT_DIR = "extracted_personas"
MIN_STRING_LENGTH = 500  # Prompts are usually long
MODEL_ID = "gemini-2.0-flash"

client = genai.Client(http_options={'api_version': 'v1alpha'})

# --- THE PROMPT MINER ---
def extract_string_literals(filepath):
    print(f"--- Reading {filepath} ---")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Regex to find double-quoted or single-quoted strings (basic approximation for minified JS)
    # We look for large chunks of text that look like prompts
    print("--- Scanning for large text blobs (this may take a moment) ---")
    
    # This regex looks for string literals. It's not a perfect JS parser but works for mining.
    # We capture typical prompt markers to filter noise.
    candidates = []
    
    # Strategy: Split by quotes and filter by length. faster than complex regex on minified files.
    fragments = re.split(r'["`]', content)
    
    for frag in fragments:
        if len(frag) > MIN_STRING_LENGTH:
            # simple heuristic: Prompts usually contain "You are" or "Assistant" or "Tool"
            if " " in frag and ("You are" in frag or "function" in frag or "context" in frag):
                candidates.append(frag)
                
    print(f"✅ Found {len(candidates)} candidate strings > {MIN_STRING_LENGTH} chars.")
    return candidates

# --- THE GEMINI ANALYZER ---
def analyze_candidate(text_chunk, index):
    prompt = f"""
    I am reverse engineering a minified AI application. 
    Below is a raw string extracted from the code. 
    
    Determine if this is a **System Prompt** or a **Persona Definition** for an AI Agent.
    
    If it is NOT a prompt (e.g. it's just license text, error messages, or documentation), reply with "NO".
    
    If it IS a prompt:
    1. Identify the Persona Name (e.g. "Planner", "Coder", "Architect").
    2. Extract the clean text.
    3. Format it as Markdown.
    
    --- RAW TEXT START ---
    {text_chunk[:15000]} 
    --- RAW TEXT END ---
    """
    # Note: Truncating to 15k chars to be safe, though Flash handles 1M.
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "NO"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    candidates = extract_string_literals(TARGET_FILE)
    
    print(f"--- analyzing {len(candidates)} candidates with {MODEL_ID} ---")
    
    found_count = 0
    for i, candidate in enumerate(candidates):
        print(f"Processing candidate {i+1}/{len(candidates)} (Length: {len(candidate)})...", end="\r")
        
        result = analyze_candidate(candidate, i)
        
        if result and not result.strip().startswith("NO"):
            found_count += 1
            # Try to guess a filename from the response
            filename = f"persona_{i}.md"
            if "Planner" in result: filename = "agent_planner.md"
            elif "Architect" in result: filename = "agent_architect.md"
            elif "Engineer" in result or "Coder" in result: filename = "agent_engineer.md"
            
            with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
                f.write(result)
            print(f"\n✅ MATCH FOUND! Saved to {filename}")

    print(f"\n\n--- Extraction Complete. Found {found_count} personas. ---")
