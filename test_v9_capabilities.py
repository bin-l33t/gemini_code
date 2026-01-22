import json
import os
import time
import pytest


def test_bash_command_mixed_output():
    # Create a dummy file for testing
    test_file = "production_test.txt"
    content = "Test content\n"
    with open(test_file, "w") as f:
        f.write(content)

    # Construct the command to execute, which includes mixed output
    command = f'echo "✔" && echo {{\"status\": \"running\"}} && cat {test_file}'

    # Execute the command
    result = default_api.Bash(command=command)

    # Check the return code
    assert result["EXIT CODE"] == 0

    # Split the stdout by newline
    lines = result["stdout"].splitlines()

    # Find the line that contains the JSON output
    json_line = None
    for line in lines:
        if line.strip().startswith("{"):
            json_line = line.strip()
            break

    # Parse the JSON output
    if json_line:
        data = json.loads(json_line)
        assert data["status"] == "running"
    else:
        pytest.fail("No JSON output found in stdout")

    # Clean up the test file
    os.remove(test_file)

