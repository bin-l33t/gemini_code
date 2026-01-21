
import os
import shutil

source_dir = "."
dest_dir = os.path.expanduser("~/gemini_code_sacrafice/gemini_code")

files_to_copy = [
    "gemini_server_v8.py",
    "gemini_code.py",
    "pipeline_master.py",
    "unify_assets.py",
    "hydrate_personas.py",
    "hydrate_personas_v2.py",
    "run_re_pipeline_v3.py",
    "variable_map.json",
    "smart_map.json",
    "variable_map_final.json",
    "variable_map_sanitized.json",
    "core_tools_reconstructed.json",
    "gemini_browser_tools.json",
    "patch_tools.py",
    "reconstruct_core_tools.py",
    "audit_agent_logic.py",
    "heal_tools.py",
    "master_variable_map.json",
    "master_tool_definitions.json",
    "package.json",
    "package-lock.json",
]

dirs_to_copy = [
    "extracted_personas",
    "hydrated_personas",
]

def copy_files(files, source, destination):
    for file in files:
        source_path = os.path.join(source, file)
        destination_path = os.path.join(destination, file)
        try:
            shutil.copy2(source_path, destination_path)  # copy2 preserves metadata
            print(f"Copied {file} to {destination}")
        except FileNotFoundError:
            print(f"Warning: {file} not found in source directory.")
        except Exception as e:
            print(f"Error copying {file}: {e}")

def copy_dirs(dirs, source, destination):
    for dir in dirs:
        source_path = os.path.join(source, dir)
        destination_path = os.path.join(destination, dir)
        try:
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
            print(f"Copied directory {dir} to {destination}")
        except FileNotFoundError:
            print(f"Warning: Directory {dir} not found in source directory.")
        except Exception as e:
            print(f"Error copying directory {dir}: {e}")

if __name__ == "__main__":
    copy_files(files_to_copy, source_dir, dest_dir)
    copy_dirs(dirs_to_copy, source_dir, dest_dir)

    print("Migration complete.")
