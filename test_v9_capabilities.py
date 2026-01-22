
import unittest
import subprocess
import os
import json

class TestAgentV9(unittest.TestCase):

    def test_production_file_creation(self):
        mission = "Create a file named production_test.txt with the content AGENT_V9_VERIFIED. Use the Edit tool to create the file."
        process = subprocess.Popen(["python", "v9_final.py", mission], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return_code = process.returncode

        self.assertTrue(os.path.exists("production_test.txt"))
        self.assertIn("✅ Test Sequence Complete.".encode('utf-8'), stdout)

        try:
            result = json.loads(stdout.decode('utf-8'))
            self.assertEqual(result['verification'], 'File created and content verified.')
        except (json.JSONDecodeError, KeyError) as e:
            self.fail(f"Failed to parse JSON or find verification key: {e}")

if __name__ == '__main__':
    unittest.main()
