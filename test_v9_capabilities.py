
import subprocess
import os
import unittest

class TestV9Capabilities(unittest.TestCase):

    def test_cli_execution(self):
        env = os.environ.copy()
        result = subprocess.run(
            ["python3", "v9_final.py", "Create production_test.txt"],
            capture_output=True,
            text=True,
            env=env
        )

        self.assertEqual(result.returncode, 0, f"Return code was {result.returncode}, stderr: {result.stderr}")

        with open("alpha.log", "r") as f:
            alpha_log_content = f.read()
            self.assertIn("[THOUGHT]", alpha_log_content, "alpha.log does not contain [THOUGHT]")

        self.assertTrue(os.path.exists("production_test.txt"), "production_test.txt does not exist")

if __name__ == '__main__':
    unittest.main()
