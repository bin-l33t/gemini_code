import os

# We want to check if the hydration resulted in readable English or broken code
TARGET_PERSONA = "hydrated_personas/agent_engineer.md"

def audit_persona():
    if not os.path.exists(TARGET_PERSONA):
        print(f"❌ Could not find {TARGET_PERSONA}")
        return

    with open(TARGET_PERSONA, "r") as f:
        content = f.read()

    print(f"--- 📖 AUDITING {TARGET_PERSONA} (Snippet) ---")
    
    # Look for the section where tools are likely described
    # Usually "You have access to..." or "Usage:"
    snippet_start = content.find("You have access to")
    if snippet_start == -1:
        snippet_start = 0
        
    print(content[snippet_start:snippet_start+1000])
    
    print("\n--- 🔍 LOGIC CHECK ---")
    # Check for common hallucination triggers
    if "${" in content:
        print("⚠️  WARNING: Unhydrated variables still present (e.g. ${A})")
    else:
        print("✅ CLEAN: No raw variables found.")
        
    if "Bash" in content and "Edit" in content:
        print("✅ LOOKS GOOD: Core tool names 'Bash' and 'Edit' appear in text.")

if __name__ == "__main__":
    audit_persona()
