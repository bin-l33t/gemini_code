#!/bin/bash

# Configuration
SRC_DIR="/home/ubuntu/gemini_code"
TARGET_DIR="/home/ubuntu/gemini_code_sacrafice/gemini_code"

echo "🚀 Starting Streamlined Deployment to Sacrifice Directory..."

# 1. Clean and Recreate Target Directory
if [ -d "$TARGET_DIR" ]; then
    echo "🧹 Cleaning existing target directory..."
    rm -rf "$TARGET_DIR"
fi
mkdir -p "$TARGET_DIR"
echo "✅ Target directory ready: $TARGET_DIR"

# 2. Migration: Copy ONLY the Golden Path files
# We ignore the old 'v1' scripts and 'audit' messes.
echo "📦 Migrating essential files..."

FILES_TO_COPY=(
    # The Orchestrator
    "pipeline_orchestrator.py"
    
    # Utilities & Setup
    "test_genai.py"
    "parse_usage.py"
    "requirements.txt"  # If you have one, otherwise ignore
    
    # Step 2: Mining (Prompt Extraction)
    "mine_prompts.py"
    
    # Step 3: Hunting (Variable Identification)
    "smart_hunt.py"
    
    # Step 4: Merging Hunt Results
    "merge_hunt_results.py"
    
    # Step 5: Sanitization
    "sanitize_map.py"
    "master_variable_map.json" # Copy existing map as a baseline if valid
    
    # Step 6: Hydration
    "hydrate_personas_v2.py"
    
    # Step 7 & 8: Tool Extraction & Merging
    "extract_schemas_full.py"
    "merge_tools.py"
    
    # Step 9: Audit/Verification
    "verify_logic_with_gemini.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$SRC_DIR/$file" ]; then
        cp "$SRC_DIR/$file" "$TARGET_DIR/"
        echo "   -> Copied $file"
    else
        echo "   ⚠️ Warning: $file not found in source (might be generated later)"
    fi
done

# 3. Setup Node Environment & Download Target
echo "📥 Installing @anthropic-ai/claude-code in target..."
cd "$TARGET_DIR"
# Initialize a dummy package.json to avoid warnings
echo '{"name": "gemini-reverse-engineer", "version": "1.0.0"}' > package.json
# Install the package to be reverse-engineered
npm install @anthropic-ai/claude-code --silent
echo "✅ npm package installed."

# 4. Execution
echo "🔥 executing Streamlined Pipeline..."
# We run the orchestrator which handles the sequence
python3 pipeline_orchestrator.py

echo "✨ Deployment and Execution Complete. Check $TARGET_DIR for results."
