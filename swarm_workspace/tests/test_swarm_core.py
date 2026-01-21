import unittest
import os
from gemini_swarm import tools, core

class TestSwarmCore(unittest.TestCase):
    
    def test_bash_tool_execution(self):
        """Verify the Bash tool can execute simple commands."""
        result = tools.Bash("echo 'hello world'")
        self.assertIn("hello world", result)
        self.assertIn("EXIT_CODE: 0", result)

    def test_edit_tool(self):
        """Verify the Edit tool can write files."""
        test_file = "test_output.txt"
        test_content = "swarm test content"
        tools.Edit(test_file, test_content)
        
        with open(test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, test_content)
        os.remove(test_file)

    def test_inspect_port_free(self):
        """Verify InspectPort reports free for an unused high port."""
        result = tools.InspectPort(12345)
        self.assertIn("PORT_STATUS: FREE", result)

    def test_core_initialization(self):
        """Verify core.run_mission handles missing personas gracefully."""
        # Test with a non-existent persona path to trigger fallback logic
        try:
            core.run_mission("hello", persona_path="non_existent.md")
        except Exception as e:
            self.fail(f"core.run_mission raised {type(e).__name__} unexpectedly!")

if __name__ == "__main__":
    unittest.main()
