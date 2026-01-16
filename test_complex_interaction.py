import asyncio
from google import genai
from google.genai import types

client = genai.Client(http_options={'api_version': 'v1alpha'})
MODEL = "gemini-2.0-flash"

# Define a mock toolset for the test
tools = [
    {
        "name": "Bash",
        "description": "Execute a bash command",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}}
    },
    {
        "name": "Planner",
        "description": "Update the plan",
        "parameters": {"type": "object", "properties": {"task": {"type": "string"}}}
    }
]

async def run_test():
    print("--- 🧪 Testing Complex Interaction Loop ---")
    
    # Simulate User Input
    chat = client.chats.create(model=MODEL)
    
    # 1. Send Instruction
    print("User: Please check the current directory and then plan a cleanup.")
    response = chat.send_message(
        message="Please check the current directory and then plan a cleanup.",
        config=types.GenerateContentConfig(tools=tools)
    )
    
    # 2. Check for Tool Call (Expecting Bash)
    part = response.candidates[0].content.parts[0]
    if part.function_call:
        fc = part.function_call
        print(f"🤖 Model: Call Tool [{fc.name}] args={fc.args}")
        
        if fc.name == "Bash":
            print("✅ PASS: Model tried to check directory.")
            # Mock Response
            tool_resp = "file1.txt\nfile2.tmp\nscript.py"
            print(f"🖥️  System: {tool_resp}")
            
            # 3. Send Tool Output back
            response2 = chat.send_message(
                message=types.Part.from_function_response(
                    name="Bash",
                    response={"result": tool_resp}
                ),
                config=types.GenerateContentConfig(tools=tools)
            )
            
            # 4. Expecting Planner
            part2 = response2.candidates[0].content.parts[0]
            if part2.function_call and part2.function_call.name == "Planner":
                print(f"🤖 Model: Call Tool [{part2.function_call.name}] args={part2.function_call.args}")
                print("✅ PASS: Model transitioned from Action -> Planning.")
            else:
                print(f"⚠️  FAIL: Model did not plan. Got: {part2.text}")
        else:
            print("⚠️  FAIL: Model did not start with Bash.")
    else:
        print("⚠️  FAIL: Model did not call a tool.")

if __name__ == "__main__":
    asyncio.run(run_test())
