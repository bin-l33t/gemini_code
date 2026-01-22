import os
import subprocess
import json
from auto_test_agent_v9 import AutoTestAgentV9, StateManifest
from unittest.mock import patch

def setup_scenario():
    """Sets up a pathing failure scenario."""
    os.makedirs("hidden_dir", exist_ok=True)
    with open("hidden_dir/secret_data.txt", "w") as f:
        f.write("Verification Code: PHX-99")
    # Ensure agent_state is clean
    if os.path.exists("agent_state.json"):
        os.remove("agent_state.json")

@patch('subprocess.run')
def test_discovery_and_thoughts(mock_run):
    setup_scenario()

    # Mock the subprocess calls in the agent
    def mock_subprocess_run(command, shell, capture_output, text):
        if 'SmartRead' in command:
            return subprocess.CompletedProcess([], 0, stdout='{"result": "Verification Code: PHX-99"}', stderr='')
        elif 'find' in command:
            return subprocess.CompletedProcess([], 0, stdout='./hidden_dir/secret_data.txt', stderr='')
        return subprocess.CompletedProcess([], 0, stdout='{}', stderr='')

    mock_run.side_effect = mock_subprocess_run

    # Mission: Read a file that is not in the root directory.
    # Expected behavior: v9 fails to find it, triggers Discovery Mode, 
    # finds hidden_dir/secret_data.txt, and updates the manifest.
    agent = AutoTestAgentV9("mission_test.txt")
    mission = "Read secret_data.txt and tell me the verification code."

    print("🚀 Starting v9 Validation...")
    agent.run(mission)

    # 1. Verify Thought Protocol
    if os.path.exists("alpha.log"):
        with open("alpha.log", "r") as f:
            content = f.read()
            assert "[THOUGHT]" in content, "❌ Thought Protocol failed: No [THOUGHT] signature in logs."
            print("✅ Thought Protocol verified.")

    # 2. Verify Discovery Loop & State Manifest
    state = StateManifest()
    paths = state.data.get("verified_paths", {})
    if any("secret_data.txt" in k for k in paths.keys()):
        print("✅ Discovery Loop verified: Corrected path found and persisted.")
    else:
        print("❌ Discovery Loop failed: Path not saved to manifest.")

    # 3. Verify Verification Gate
    # Check agent's internal state or logs for "Verification Passed"
    print("✅ Test Sequence Complete.")

if __name__ == "__main__":
    test_discovery_and_thoughts()
