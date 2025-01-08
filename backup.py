import sys
import os
import tarfile
import yaml

def validate_args(args):
    yaml_path = None
    override = False

    for arg in args:
        if arg.startswith("--") or arg.startswith("-"):
            if arg in ("--override", "-O"):
                override = True
            else:
                print(f"Unknown argument: {arg}")
                sys.exit(1)
        elif yaml_path is None:
            yaml_path = arg

    return yaml_path, override

def check_env_vars(filepath):
    if "$" in filepath or "~" in filepath:
        print("Error: Environment variables (e.g., $HOME or $USER) are not allowed in the filepath.")
        sys.exit(1)

def validate_yaml_path(yaml_path):
    if not (yaml_path.endswith(".yml") or yaml_path.endswith(".yaml")):
        print("Error: The filepath must end with .yml or .yaml.")
        sys.exit(1)

    if not os.path.exists(yaml_path):
        print(f"Error: The file '{yaml_path}' does not exist.")
        sys.exit(1)

def process_yaml(yaml_path, override):
    try:
        with open(yaml_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is None:
                print("Error: The YAML file is empty.")
                sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: YAML syntax error in file '{yaml_path}'. {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to parse YAML file. {e}")
        sys.exit(1)

    for src, dest in data.items():
        # Validate that src exists
        if not os.path.exists(src):
            print(f"Source path '{src}' does not exist. Skipping.")
            continue

        # Validate that the parent directory of dest exists
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            print(f"Destination directory '{dest_dir}' does not exist. Skipping.")
            continue

        # Check if the output file already exists
        if os.path.exists(dest):
            if override:
                print(f"Overriding existing file: {dest}")
            else:
                print(f"File '{dest}' already exists. Skipping.")
                continue

        try:
            with tarfile.open(dest, "w:gz") as tar:
                tar.add(src, arcname=os.path.basename(src))
            print(f"Compressed '{src}' to '{dest}' successfully.")
        except Exception as e:
            print(f"Error: Failed to compress '{src}' to '{dest}'. {e}")

def main():
    # Validate arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py [--override|-O] <yaml_path>")
        sys.exit(1)

    yaml_path, override = validate_args(sys.argv[1:])

    if not yaml_path:
        print("Error: No YAML file path provided.")
        sys.exit(1)

    # Validate filepath and environment variables
    check_env_vars(yaml_path)
    validate_yaml_path(yaml_path)

    # Process YAML and create compressed files
    process_yaml(yaml_path, override)

if __name__ == "__main__":
    main()

