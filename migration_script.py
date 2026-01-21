
import os
import shutil

source_dir = os.path.expanduser('~/gemini_code')
dest_dir = os.path.expanduser('~/gemini_code_sacrafice/gemini_code')

files_to_copy = [
    'gemini_server_v8.py',
    'gemini_code.py',
    'pipeline_master.py',
    'run_re_pipeline_v3.py',
    'unify_assets.py',
    'hydrate_personas_v2.py',
    'hydrate_personas.py',
    'patch_tools.py',
    'reconstruct_core_tools.py',
    'audit_agent_logic.py',
    'audit_tools.py',
    'heal_tools.py',
    'variable_map_final.json',
    'smart_map.json',
    'variable_map.json',
    'core_tools_reconstructed.json',
    'package.json',
    'requirements.txt'
]

dirs_to_copy = [
    'extracted_personas',
    'hydrated_personas'
]

# Copy files
for file in files_to_copy:
    source_file = os.path.join(source_dir, file)
    dest_file = os.path.join(dest_dir, file)
    try:
        shutil.copy2(source_file, dest_file)  # copy2 preserves metadata
        print(f"Copied file: {file}")
    except FileNotFoundError:
        print(f"Warning: File not found: {file}")
    except Exception as e:
        print(f"Error copying file {file}: {e}")

# Copy directories recursively
for dir in dirs_to_copy:
    source_dir_path = os.path.join(source_dir, dir)
    dest_dir_path = os.path.join(dest_dir, dir)
    try:
        shutil.copytree(source_dir_path, dest_dir_path)
        print(f"Copied directory: {dir}")
    except FileNotFoundError:
        print(f"Warning: Directory not found: {dir}")
    except FileExistsError:
        print(f"Warning: Directory already exists: {dir}")
    except Exception as e:
        print(f"Error copying directory {dir}: {e}")

# Generate manifest
print("\nManifest of the new 'Gold Master' directory:")
for root, _, files in os.walk(dest_dir):
    for file in files:
        print(os.path.join(root, file))
