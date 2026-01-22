"""Test file for verifying agent v9 capabilities."""

import unittest
import subprocess
import json
import os

class TestAgentV9Capabilities(unittest.TestCase):

    def test_v9_final(self):
        # Define a simple mission
        mission = "Write 'hello world' to a file named output.txt"

        # Run v9_final.py with the mission
        process = subprocess.Popen(['python3', 'v9_final.py', mission], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return_code = process.returncode

        # Check for errors
        self.assertEqual(return_code, 0, f"v9_final.py failed with error: {stderr.decode()}")

        # Check if the file was created and contains the correct content
        try:
            with open("output.txt", "r") as f:
                content = f.read().strip()
            self.assertEqual(content, "hello world", "File content does not match the expected output.")
        except FileNotFoundError:
            self.fail("output.txt was not created.")
        finally:
            # Clean up the file
            if os.path.exists("output.txt"):
                os.remove("output.txt")

if __name__ == '__main__':
    unittest.main()
