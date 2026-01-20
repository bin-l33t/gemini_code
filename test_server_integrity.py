import unittest
import urllib.request
import urllib.parse
import urllib.error
import time
import sys

BASE_URL = "http://localhost:8888"

class TestGeminiServer(unittest.TestCase):
    def setUp(self):
        """Verify server is reachable before running tests."""
        try:
            with urllib.request.urlopen(BASE_URL, timeout=5) as response:
                self.assertEqual(response.status, 200, "Server root did not return 200")
        except urllib.error.URLError as e:
            self.fail(f"Could not connect to server at {BASE_URL}. Is it running? Error: {e}")

    def test_get_root(self):
        """Test GET / returns the HTML console."""
        with urllib.request.urlopen(BASE_URL) as response:
            html = response.read().decode('utf-8')
            self.assertIn("<title>Gemini Code Console</title>", html)
            self.assertIn("gemini-2.0-flash", html)

    def test_post_prompt(self):
        """Test POST / with a prompt updates the history."""
        # 1. Reset history first
        reset_req = urllib.request.Request(f"{BASE_URL}/reset", method="POST")
        with urllib.request.urlopen(reset_req) as response:
            self.assertEqual(response.status, 200) # urllib follows 303 redirect to / which returns 200
        
        # 2. Post a prompt
        test_prompt = "TEST_INTEGRITY_CHECK_" + str(int(time.time()))
        data = urllib.parse.urlencode({
            "prompt": test_prompt,
            "model_choice": "gemini-2.0-flash",
            "uploaded_file": "" 
        }).encode('utf-8')
        
        req = urllib.request.Request(BASE_URL, data=data, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                self.assertEqual(response.status, 200)
                # Verify the prompt appears in the rendered HTML history
                html = response.read().decode('utf-8')
                self.assertIn(test_prompt, html, "Posted prompt was not found in response HTML")
        except urllib.error.HTTPError as e:
            self.fail(f"POST request failed: {e}")

if __name__ == "__main__":
    print(f"🔍 Running Integrity Tests against {BASE_URL}...")
    unittest.main()
