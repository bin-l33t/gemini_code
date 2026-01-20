import os
import subprocess

# --- Configuration ---
AGENT_SCRIPT = "auto_test_agent_v6.py"
MISSION_FILE = "mission_verify_server.txt"
TEST_SUITE_FILE = "test_server_integrity.py"
SERVER_PORT = 8888

# --- The Test Suite Code (Standard Lib Only) ---
# This code will be embedded into the mission prompt
TEST_SUITE_CODE = f'''import unittest
import urllib.request
import urllib.parse
import urllib.error
import time
import sys

BASE_URL = "http://localhost:{SERVER_PORT}"

class TestGeminiServer(unittest.TestCase):
    def setUp(self):
        """Verify server is reachable before running tests."""
        try:
            with urllib.request.urlopen(BASE_URL, timeout=5) as response:
                self.assertEqual(response.status, 200, "Server root did not return 200")
        except urllib.error.URLError as e:
            self.fail(f"Could not connect to server at {{BASE_URL}}. Is it running? Error: {{e}}")

    def test_get_root(self):
        """Test GET / returns the HTML console."""
        with urllib.request.urlopen(BASE_URL) as response:
            html = response.read().decode('utf-8')
            self.assertIn("<title>Gemini Code Console</title>", html)
            self.assertIn("gemini-2.0-flash", html)

    def test_post_prompt(self):
        """Test POST / with a prompt updates the history."""
        # 1. Reset history first
        reset_req = urllib.request.Request(f"{{BASE_URL}}/reset", method="POST")
        with urllib.request.urlopen(reset_req) as response:
            self.assertEqual(response.status, 200) # urllib follows 303 redirect to / which returns 200
        
        # 2. Post a prompt
        test_prompt = "TEST_INTEGRITY_CHECK_" + str(int(time.time()))
        data = urllib.parse.urlencode({{
            "prompt": test_prompt,
            "model_choice": "gemini-2.0-flash",
            "uploaded_file": "" 
        }}).encode('utf-8')
        
        req = urllib.request.Request(BASE_URL, data=data, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, 200)
                # Verify the prompt appears in the rendered HTML history
                html = response.read().decode('utf-8')
                self.assertIn(test_prompt, html, "Posted prompt was not found in response HTML")
        except urllib.error.HTTPError as e:
            self.fail(f"POST request failed: {{e}}")

if __name__ == "__main__":
    print(f"🔍 Running Integrity Tests against {{BASE_URL}}...")
    unittest.main()
'''

# --- Generate the Mission Prompt ---
mission_prompt = f"""
TARGET: Diagnose and Verify `gemini_server_v8.py` on Port {SERVER_PORT}.

OBJECTIVE:
The user reports "basic requests are failing" on the server. You must deploy a test suite to verify the server endpoints.

INSTRUCTIONS:
1. **INSPECT**: Use `InspectPort({SERVER_PORT})` to confirm `gemini_server_v8.py` is actually the process listening on the port.
2. **DEPLOY**: Create a file named `{TEST_SUITE_FILE}` containing the EXACT python code below.
3. **EXECUTE**: Run the test suite using `Bash("python3 {TEST_SUITE_FILE}")`.
4. **ANALYZE**: 
   - If the tests PASS, report "STATUS: GREEN".
   - If the tests FAIL, use `Bash("cat server_v8.log")` (or similar) to check the server logs if they exist, or provide a hypothesis on why it failed based on the test output.

--- BEGIN TEST SUITE CODE ---
{TEST_SUITE_CODE}
--- END TEST SUITE CODE ---
"""

def main():
    print(f"🚀 Initializing Test Orchestration for Port {SERVER_PORT}...")
    
    # 1. Write the Mission File
    print(f"[1/3] Generating mission file: {MISSION_FILE}")
    with open(MISSION_FILE, "w") as f:
        f.write(mission_prompt)
        
    # 2. Check for Agent
    if not os.path.exists(AGENT_SCRIPT):
        print(f"❌ Error: {AGENT_SCRIPT} not found in current directory.")
        return

    # 3. Launch the Agent
    print(f"[2/3] Launching Agent subprocess...")
    print(f"      Command: python3 {AGENT_SCRIPT} {MISSION_FILE}")
    print("="*60)
    
    try:
        subprocess.run(["python3", AGENT_SCRIPT, MISSION_FILE], check=True)
        print("="*60)
        print("[3/3] Orchestration Complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Agent execution failed with exit code {e.returncode}")
    except KeyboardInterrupt:
        print("\n🛑 Orchestration stopped by user.")

if __name__ == "__main__":
    main()
