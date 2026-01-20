import unittest
import urllib.request
import urllib.parse
import urllib.error
import time
import socket

# Configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8888
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

class TestGeminiServerFunctions(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Wait for server to be ready before running tests."""
        print(f"Testing connection to {BASE_URL}...")
        for _ in range(5):
            try:
                with urllib.request.urlopen(BASE_URL, timeout=2) as response:
                    if response.status == 200:
                        print("✅ Server is reachable.")
                        return
            except Exception:
                time.sleep(1)
        print("❌ Server appears down. Please start 'gemini_server_v8.py' first.")
        # We continue anyway to show failures if it's down

    def test_01_health_check(self):
        """Test if the server loads the main page (GET request)."""
        try:
            with urllib.request.urlopen(BASE_URL) as response:
                self.assertEqual(response.status, 200)
                content = response.read().decode('utf-8')
                self.assertIn("Gemini Code Console", content)
        except Exception as e:
            self.fail(f"Health check failed: {e}")

    def test_02_post_basic_prompt(self):
        """Test submitting a simple text prompt (No file)."""
        # This mocks a standard form submission where 'uploaded_file' might be empty
        data = urllib.parse.urlencode({
            "prompt": "Hello Check 1",
            "model_choice": "gemini-2.0-flash",
            "uploaded_file": ""  # Simulating empty file field
        }).encode('utf-8')
        
        req = urllib.request.Request(BASE_URL, data=data, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, 200)
                content = response.read().decode('utf-8')
                self.assertIn("Hello Check 1", content)
        except urllib.error.HTTPError as e:
            self.fail(f"POST with empty file failed (Crash Reproduced?): {e}")

    def test_03_post_no_file_field(self):
        """Test submitting a prompt where 'uploaded_file' key is completely missing."""
        data = urllib.parse.urlencode({
            "prompt": "Hello Check 2",
            "model_choice": "gemini-2.0-flash"
        }).encode('utf-8')
        
        req = urllib.request.Request(BASE_URL, data=data, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, 200)
                content = response.read().decode('utf-8')
                self.assertIn("Hello Check 2", content)
        except urllib.error.HTTPError as e:
            self.fail(f"POST missing 'uploaded_file' key failed: {e}")

    def test_04_reset_history(self):
        """Test the history reset function."""
        req = urllib.request.Request(f"{BASE_URL}/reset", method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, 200)
        except Exception as e:
            self.fail(f"Reset failed: {e}")

if __name__ == "__main__":
    unittest.main()
