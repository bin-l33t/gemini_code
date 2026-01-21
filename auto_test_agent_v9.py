import json
import os
import subprocess
import sys
from datetime import datetime

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
    def __init__(self):
        self.history = []

    def record(self, hypothesis, expected_outcome):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "hypothesis": hypothesis,
            "expectation": expected_outcome
        }
        self.history.append(entry)
        print(f"🤔 [THOUGHT]: {hypothesis}")

class AutoTestAgentV9:
    def __init__(self, mission_file):
        self.state = StateManifest()
        self.thoughts = ThoughtEngine()
        # ... logic to initialize Gemini model and tools ...

    def execute_bash(self, command):
        """Enhanced bash tool with Discovery Mode and State Injection."""
        # Inject known environment variables (e.g., PYTHONPATH)
        if "PYTHONPATH" in self.state.data["env_vars"]:
            command = f"export PYTHONPATH={self.state.data['env_vars']['PYTHONPATH']} && {command}"
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Self-Correction: Discovery Loop
        if result.returncode != 0 and ("No such file" in result.stderr or "cannot stat" in result.stderr):
            print("🕵️ Path mismatch detected. Initiating Discovery Loop...")
            self.discovery_mode(command)
            
        return result

    def verification_gate(self, proof_command):
        """Final check to ensure the mission's intent was realized."""
        print(f"🛡️ [VERIFICATION GATE]: Running {proof_command}...")
        res = self.execute_bash(proof_command)
        if res.returncode == 0:
            print("✅ Verification Passed.")
            return True
        print("❌ Verification Failed. Re-evaluating mission...")
        return False
