import os
import re
import argparse
import subprocess

def apply_patch_to_files(module_names, change_file, search_dir, exclude_dirs):
    # Compile regex patterns for each module name
    patterns = [re.compile(rf'.*{module_name}\s*#?\s*\(') for module_name in module_names]

    # List to store files that contain any of the specified module instances
    files_to_patch = set()

    # Walk through the directory to find `.v` files, following links by default
    for root, dirs, files in os.walk(search_dir, followlinks=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        for file in files:
            if file.endswith(".v"):
                file_path = os.path.join(root, file)
                
                # Check if any of the specified module instances are in the file
                with open(file_path, 'r') as f:
                    content = f.read()
                    if any(pattern.search(content) for pattern in patterns):
                        files_to_patch.add(file_path)

    # Apply patch to each identified file
    for file in files_to_patch:
        print(f"Preparing to edit {file} in Perforce...")

        # Run `p4 edit` on the file to open it for editing
        #try:
        #    subprocess.run(["p4", "edit", file], check=True)
        #    print(f"{file} checked out for editing.")
        #except subprocess.CalledProcessError as e:
        #    print(f"Failed to check out {file} for editing: {e}")
        #    continue  # Skip to the next file if `p4 edit` fails

        # Apply the patch to the file
        print(f"Applying patch to {file}...")
        try:
            result = subprocess.run(
                ["patch", "-p0", file],
                input=open(change_file, 'rb').read(),
                check=True
            )
            print(f"Patch applied successfully to {file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to apply patch to {file}: {e}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Apply patch to Verilog files with specific module instances.")
    parser.add_argument("module_names", nargs="+", help="Names of the modules to search for in Verilog files.")
    parser.add_argument("change_file", help="Path to the change log file containing the patch.")
    parser.add_argument("search_dir", help="Directory to search for Verilog files.")
    parser.add_argument(
        "--exclude_dirs", nargs="*", default=[], help="Directories to exclude from the search."
    )

    # Parse arguments
    args = parser.parse_args()

    # Apply patch to files with specified module instances
    apply_patch_to_files(
        args.module_names, args.change_file, args.search_dir, args.exclude_dirs
    )
