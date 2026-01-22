import json
import os
import re
import subprocess
import sys
from datetime import datetime
from gemini_swarm import tools

class StateManifest:
    """Manages persistent context and environmental facts."""
    def __init__(self, path="agent_state.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {"verified_paths": {}, "env_vars": {}, "checkpoints": []}

    def update_fact(self, key, value):
        self.data["verified_paths"][key] = value
        self.save()

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

class ThoughtEngine:
    """Captures the agent's mental model before tool calls."""
    def __init__(self, log_path="alpha.log"):
        self.history = []
        self.log_path = log_path

    def record(self, hypothesis, expected_outcome):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "hypothesis": hypothesis,
            "expectation": expected_outcome
        }
        self.history.append(entry)
        thought_msg = f"🤔 [THOUGHT]: {hypothesis} | Expectation: {expected_outcome}"
        print(thought_msg)
        # Ensure thoughts are recorded in the log for test validation
        with open(self.log_path, "a") as f:
            f.write(thought_msg + "\n")

class AutoTestAgentV9:
    def __init__(self, mission_file):
        self.state = StateManifest()
        self.thoughts = ThoughtEngine()
        self.mission_file = mission_file
        self.max_iterations = 10
        # Integrate gemini_swarm.tools into the class
        self.available_tools = {
            "Bash": tools.Bash,
            "Edit": tools.Edit,
            "InspectPort": tools.InspectPort,
            "KillProcess": tools.KillProcess,
            "SmartRead": tools.SmartRead,
            "SpawnSubAgent": tools.SpawnSubAgent
        }
        self.model_id = 'gemini-2.0-flash'
        os.environ.get('GEMINI_API_KEY')

    def discovery_mode(self, command):
        """Parses command for filenames and updates manifest with found paths."""
        # Regex to find potential filenames with extensions
        filenames = re.findall(r"([a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+)", command)
        for filename in filenames:
            print(f"🕵️ Discovery Mode: Searching for {filename}...")
            find_cmd = f"find . -name '{filename}'"
            res = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                corrected_path = res.stdout.strip().split('\n')[0]
                print(f"✅ Found corrected path: {corrected_path}")
                self.state.update_fact(filename, corrected_path)

    def execute_bash(self, command):
        """Enhanced bash tool with Discovery Mode and State Injection."""
        # Inject known environment variables
        if "PYTHONPATH" in self.state.data["env_vars"]:
            command = f"export PYTHONPATH={self.state.data['env_vars']['PYTHONPATH']} && {command}"
        
        # Inject discovered paths into the command
        for filename, full_path in self.state.data["verified_paths"].items():
            if filename in command and full_path not in command:
                command = command.replace(filename, full_path)

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Self-Correction Trigger
        if result.returncode != 0 and ("No such file" in result.stderr or "cannot stat" in result.stderr):
            print("🕵️ Path mismatch detected. Initiating Discovery Loop...")
            self.discovery_mode(command)
            # Retry after discovery
            return self.execute_bash(command) 
            
        return result

    def verification_gate(self, proof_command):
        """Final check to ensure the mission's intent was realized."""
        if not proof_command: return False
        print(f"🛡️ [VERIFICATION GATE]: Running {proof_command}...")
        res = self.execute_bash(proof_command)
        return res.returncode == 0

    def run(self, mission):
        """Core loop implementing Thought Protocol and model interaction."""
        iterations = 0
        current_observation = "Initial state."
        
        while iterations < self.max_iterations:
            iterations += 1
            print(f"\n🔄 Iteration {iterations}/{self.max_iterations}")

            # 1. Call Gemini Model (simulated logic for the loop)
            # In production, this would use a core utility to call gemini-3-pro
            prompt = f"Mission: {mission}\nState: {self.state.data}\nLast Observation: {current_observation}"
            
            # 2. Parse Thought and Tool (Thought Protocol)
            # Example response structure expected from gemini-3-pro:
            # { \"thought\": \"...\", \"expectation\": \"...\", \"tool\": \"Bash\", \"input\": \"...\", \"verification\": \"...\" }
            
            # Placeholder for actual model response parsing:
            # response_data = {\"thought\": \"Inspect directory\", \"expectation\": \"Find files\", \"tool\": \"Bash\", \"input\": \"ls\"} 
            
            # TODO: Replace with actual call to Gemini and JSON parsing
            try:
                # Simulate Gemini response (replace with actual API call)
                # response_json = \'{\"thought\": \"Inspect directory\", \"expectation\": \"Find files\", \"tool\": \"Bash\", \"input\": \"ls\"}\'
                
                # For testing, let's assume the response is just the tool and input
                response_json = '{"thought": "List files", "expectation": "See file names", "tool": "Bash", "input": "ls"}'
                response_data = json.loads(response_json)
            except json.JSONDecodeError as e:
                current_observation = f"Error decoding JSON response: {e}"
                continue
            
            self.thoughts.record(response_data['thought'], response_data['expectation'])

            # 3. Execute Tools
            tool_name = response_data.get("tool")
            tool_input = response_data.get("input")
            if tool_name == "Bash":
                res = self.execute_bash(tool_input)
                current_observation = f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
            elif tool_name in self.available_tools:
                current_observation = self.available_tools[tool_name](tool_input)
            else:
                current_observation = f"Error: Tool '{tool_name}' not found."
            
            # 4. Early Stopping Check
            if self.verification_gate(response_data.get("verification")):
                print("✅ Mission accomplished. Stopping early.")
                break

if __name__ == "__main__":
    # Handle command-line mission input
    if len(sys.argv) < 2:
        print("Usage: python3 auto_test_agent_v9.py '<mission_text>'")
        sys.exit(1)
        
    mission_text = sys.argv[1]
    agent = AutoTestAgentV9("mission_v9.json")
    agent.run(mission_text)
