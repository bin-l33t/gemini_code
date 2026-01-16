import os
import re
import json
import argparse
from google import genai
from google.genai import types

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Mine System Prompts from Minified JS")
parser.add_argument("--limit", type=int, default=200, help="Maximum number of candidate strings to process (Default: 200 for full run)")
args = parser.parse_args()

# --- CONFIGURATION ---
TARGET_FILE = "node_modules/@anthropic-ai/claude-code/cli.js"
OUTPUT_DIR = "extracted_personas"
MIN_STRING_LENGTH = 500  # Prompts are usually long
MAX_CANDIDATES = args.limit
MODEL_ID = "gemini-2.0-flash"

client = genai.Client(http_options={'api_version': 'v1alpha'})

# --- THE PROMPT MINER ---
def extract_string_literals(filepath):
    print(f"--- Reading {filepath} ---")
    if not os.path.exists(filepath):
        print(f"❌ Error: File {filepath} not found.")
        return []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("--- Scanning for large text blobs ---")
    candidates = []
    
    # Strategy: Split by quotes and filter by length
    fragments = re.split(r'["`]', content)
    
    for frag in fragments:
        if len(frag) > MIN_STRING_LENGTH:
            # Heuristic: Prompts usually contain "You are" or "Assistant" or "Tool"
            if " " in frag and ("You are" in frag or "function" in frag or "context" in frag):
                candidates.append(frag)
    
    # OPTIMIZATION: Sort by length (descending) to find main prompts first
    candidates.sort(key=len, reverse=True)
    
    print(f"✅ Found {len(candidates)} candidate strings > {MIN_STRING_LENGTH} chars.")
    if len(candidates) > MAX_CANDIDATES:
        print(f"⚠️  Limiting to top {MAX_CANDIDATES} longest candidates (Limit set by --limit).")
        return candidates[:MAX_CANDIDATES]
        
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
    
    if not candidates:
        print("❌ No candidates found or file missing.")
        exit(1)

    print(f"--- Analyzing {len(candidates)} candidates with {MODEL_ID} ---")
    
    found_count = 0
    for i, candidate in enumerate(candidates):
        print(f"Processing candidate {i+1}/{len(candidates)} (Length: {len(candidate)})...")
        
        result = analyze_candidate(candidate, i)
        
        if result and not result.strip().startswith("NO"):
            found_count += 1
            # Try to guess a filename from the response
            filename = f"persona_{i}.md"
            if "Planner" in result: filename = "agent_planner.md"
            elif "Architect" in result: filename = "agent_architect.md"
            elif "Engineer" in result or "Coder" in result: filename = "agent_engineer.md"
            elif "Guide" in result: filename = "agent_guide.md"
            
            with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
                f.write(result)
            print(f"   ✅ MATCH: Saved to {filename}")

    print(f"\n--- Extraction Complete. Found {found_count} personas. ---")
