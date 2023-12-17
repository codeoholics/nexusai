import json
import shutil
import sys

def update_pipfile(pipfile_path, pipfile_lock_path):
    # Backup the original Pipfile
    shutil.copy(pipfile_path, pipfile_path + '.backup')

    # Load Pipfile.lock
    with open(pipfile_lock_path, 'r') as file:
        lock_data = json.load(file)

    # Extracting packages and their exact versions from Pipfile.lock
    packages_versions = {pkg.replace("-", "_"): details['version'].lstrip("==")
                         for pkg, details in lock_data['default'].items()}

    # Read the Pipfile
    with open(pipfile_path, 'r') as file:
        pipfile_lines = file.readlines()

    # Update Pipfile with exact versions
    updated_lines = []
    for line in pipfile_lines:
        if '=' in line:  # Process only lines with package definitions
            package_name = line.split('=')[0].strip().replace("-", "_")
            if package_name in packages_versions:
                updated_line = f'{package_name} = "=={packages_versions[package_name]}"\n'
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)  # Append the line unchanged if the package is not in Pipfile.lock
        else:
            updated_lines.append(line)  # Append non-package-definition lines unchanged

    # Write the updated content back to the Pipfile
    with open(pipfile_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Pipfile has been updated with exact versions. Original Pipfile is backed up as '{pipfile_path}.backup'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        pipfile_path = "../Pipfile"
        pipfile_lock_path = "../Pipfile.lock"
        update_pipfile(pipfile_path, pipfile_lock_path)
    else:
        pipfile_path = sys.argv[1]
        pipfile_lock_path = sys.argv[2]
        update_pipfile(pipfile_path, pipfile_lock_path)
