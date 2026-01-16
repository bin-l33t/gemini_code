from google import genai
import os
import sys

def test_gemini_connection():
    print("--- 1. Checking Environment ---")
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY (or GEMINI_API_KEY) not found in environment variables.")
        return False
    print(f"✅ API Key found (starts with: {api_key[:4]}...)")

    print("\n--- 2. Initializing Client (google-genai) ---")
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized.")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

    print("\n--- 3. Testing Generation (Gemini 2.0 Flash) ---")
    try:
        # Using a basic prompt to test connectivity
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Reply with "System Operational" if you receive this.'
        )
        print(f"Response: {response.text}")
        
        if "Operational" in response.text:
            print("✅ Test PASSED: API is reachable and generating text.")
            return True
        else:
            print("⚠️ Test Warning: API returned unexpected text.")
            return True # Still technically a pass if we got text back
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
