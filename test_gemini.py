import os
import google.generativeai as genai

# 1. Get API Key from environment
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY is not set.")
    print("   Run: export GEMINI_API_KEY='your_key_here'")
else:
    # 2. Configure the client
    genai.configure(api_key=api_key)
    
    try:
        # 3. Test a simple generation
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, reply with 'System Operational' if you can read this.")
        
        print("-" * 30)
        print(f"✅ Status: {response.text.strip()}")
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
