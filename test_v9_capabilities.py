import subprocess
import unittest
import os

class TestV9Capabilities(unittest.TestCase):

    def test_v9_subprocess_call(self):
        # Hardcode the target file
        target_file = 'v9_final.py'
        
        # Construct the full path to the target file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.join(script_dir, target_file)

        # Call the subprocess with the hardcoded target file
        process = subprocess.Popen(['python', target_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Assert that the subprocess executed successfully (you might need to adjust the assertion based on the expected behavior of v9_final.py)
        self.assertEqual(process.returncode, 0, f'Subprocess failed with error: {stderr.decode()}')

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
