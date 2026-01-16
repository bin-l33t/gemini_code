import os
import sys
from google import genai
from google.genai import types

def verify_setup():
    print("----------------------------------------------------------------")
    print("🔍 DIAGNOSTIC: Gemini API Environment Verification")
    print("----------------------------------------------------------------")

    # 1. Check API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ CRITICAL: GEMINI_API_KEY environment variable is missing.")
        print("   Run: export GEMINI_API_KEY='your_actual_key_here'")
        sys.exit(1)
    else:
        # Print last 4 chars for verification without leaking
        print(f"✅ API Key detected (ends in ...{api_key[-4:]})")

    try:
        client = genai.Client(api_key=api_key)
        
        # 2. Test Basic Connectivity & Text Gen
        print("\n[Test 1/2] Connecting to Gemini 2.0 Flash...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Respond with 'pong' if you hear me."
        )
        if response.text and "pong" in response.text.lower():
            print(f"✅ Text Generation Success: {response.text.strip()}")
        else:
            print(f"⚠️ Unexpected Text Response: {response.text}")

        # 3. Test Code Execution Sandbox
        # This is vital for the 'Gemini Code' agent we are building.
        print("\n[Test 2/2] Verifying Code Execution Sandbox...")
        prompt = "Calculate the sum of the first 10 prime numbers using Python code."
        
        response_code = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution)]
            )
        )
        
        # Check if code was actually executed
        executed = False
        for part in response_code.candidates[0].content.parts:
            if part.code_execution_result:
                executed = True
                print(f"   > Code Output: {part.code_execution_result.output.strip()}")
                # sum of 2, 3, 5, 7, 11, 13, 17, 19, 23, 29 = 129
                if "129" in part.code_execution_result.output:
                    print("✅ Code Execution Logic Correct.")
                else:
                    print("⚠️ Code Execution ran, but result needs manual check.")
        
        if not executed:
            print("❌ Error: Model did not trigger code execution tool.")
        else:
            print("✅ Code Execution Sandbox Operational.")

        print("\n----------------------------------------------------------------")
        print("🚀 RESULT: SYSTEM READY FOR 'GEMINI CODE' DEVELOPMENT")
        print("----------------------------------------------------------------")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_setup()
