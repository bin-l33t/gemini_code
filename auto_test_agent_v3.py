
import os

def Edit(
    path: str,
    content: str,
) -> dict:
  """Writes content to a file (overwrites).

  Args:
    path:
    content:
  """
  expanded_path = os.path.expanduser(path)
  try:
    with open(expanded_path, "w") as f:
      f.write(content)
    return {"success": True}
  except Exception as e:
    return {"success": False, "error": str(e)}


def View(
    path: str,
) -> dict:
  """Reads a file from the filesystem.

  Args:
    path:
  """
  expanded_path = os.path.expanduser(path)
  try:
    with open(expanded_path, "r") as f:
      content = f.read()
    return {"success": True, "content": content}
  except Exception as e:
    return {"success": False, "error": str(e)}


def Bash(
    command: str,
) -> dict:
  """Executes a command in the bash shell. Use this to run python scripts.

  Args:
    command:
  """
  import subprocess
  try:
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash")
    stdout, stderr = process.communicate()
    return {"success": True, "stdout": stdout.decode(), "stderr": stderr.decode()}
  except Exception as e:
    return {"success": False, "error": str(e)}



# Example usage (replace with your actual agent logic)
if __name__ == '__main__':
    # Create a directory
    result = Bash(command="mkdir -p ~/gemini_code_test")
    print(f"mkdir result: {result}")

    # Write a file
    file_path = "~/gemini_code_test/test_file.txt"
    file_content = "This is a test file."
    edit_result = Edit(path=file_path, content=file_content)
    print(f"Edit result: {edit_result}")

    # Read the file
    view_result = View(path=file_path)
    print(f"View result: {view_result}")

    # Clean up
    result = Bash(command="rm -rf ~/gemini_code_test")
    print(f"rm result: {result}")
