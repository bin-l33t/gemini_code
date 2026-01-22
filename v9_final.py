
import json
from gemini_swarm.tools import Bash, Edit, SmartRead
import google.generativeai as genai

class AutoTestAgentV9:
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model_name = model_name
        self.system_instruction = self._load_system_instruction()
        genai.configure(api_key="YOUR_API_KEY") # Replace with your actual API key
        self.model = genai.GenerativeModel(self.model_name)

    def _load_system_instruction(self):
        try:
            content = SmartRead(path="gemini_swarm/personas/agent_claude_code.md")["content"]
            return content
        except Exception as e:
            print(f"Error loading system instruction: {e}")
            return ""

    def get_model_response(self, prompt):
        try:
            response_text = self.model.generate_content([self.system_instruction, prompt]).text
            try:
                response_data = json.loads(response_text)
                # Ensure 'thought' is present in the response_data
                if 'thought' in response_data:
                    # Placeholder for self.thoughts.record() call
                    print(f"Recording thought: {response_data['thought']}")
                    # self.thoughts.record(response_data['thought']) # Uncomment when self.thoughts is defined
                else:
                    print("Warning: 'thought' field not found in model response.")

                # Example tool call (assuming 'tool' and relevant arguments are in response_data)
                if 'tool' in response_data:
                    tool = response_data['tool']
                    if tool == 'Edit':
                        path = response_data['path']
                        content = response_data['content']
                        Edit(path=path, content=content)
                    elif tool == 'Bash':
                        command = response_data['command']
                        Bash(command=command)
                    elif tool == 'SmartRead':
                        path = response_data['path']
                        SmartRead(path=path)
                    else:
                        print(f"Unknown tool: {tool}")
            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON response: {e}. Response text: {response_text}"
                print(error_message)
                # Log the error to alpha.log
                Bash(command=f'echo "{error_message}" >> alpha.log')
                response_data = {"error": "Malformed JSON response from model"} # Provide a fallback
            return json.dumps(response_data) # Ensure valid JSON is returned
        except Exception as e:
            print(f"Error getting model response: {e}")
            return json.dumps({"error": str(e)}) # Ensure valid JSON even on error

    def verification_gate(self, data):
        # Simulate verification, ensuring valid JSON output
        if data:
            result = {"status": "success", "message": "Verification passed"}
        else:
            result = {"status": "failed", "message": "Verification failed"}
        return json.dumps(result)

# Example usage (replace with your actual test logic)
if __name__ == "__main__":
    agent = AutoTestAgentV9()
    prompt = "Write a simple python function to add two numbers."
    response = agent.get_model_response(prompt)
    print(f"Model Response: {response}")

    # Simulate data for verification
    test_data = {"input1": 5, "input2": 10}
    verification_result = agent.verification_gate(test_data)
    print(f"Verification Result: {verification_result}")
