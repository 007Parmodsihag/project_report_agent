# agent/input_parser.py
import yaml
from pathlib import Path

class InputParser:
    """Reads and validates project data from a YAML input file."""

    # Define essential keys that must be present in the YAML file
    REQUIRED_KEYS = [
        'student_name', 'roll_number', 'project_title', 'supervisor_name',
        'department', 'college', 'submission_month_year', 'course_code'
        # Add other truly essential keys if needed
    ]
    # Define keys expected to be lists
    LIST_KEYS = [
        'objectives', 'conclusions_future_scope',
        'introduction_points', 'literature_review_ideas' # Add others if defined
    ]
    # Define keys that might contain file paths, useful for validation
    PATH_KEYS = ['logo_image_path']

    def __init__(self, filepath: str):
        """
        Initializes the parser with the path to the YAML file.

        Args:
            filepath (str): The path to the project_data.yaml file.
        """
        self.filepath = Path(filepath)

    def load_and_validate(self) -> dict:
        """
        Loads the YAML file, performs validation, and returns the data.

        Returns:
            dict: The parsed project data.

        Raises:
            FileNotFoundError: If the input file does not exist.
            yaml.YAMLError: If the file cannot be parsed as YAML.
            ValueError: If validation checks fail (missing keys, wrong types).
        """
        if not self.filepath.is_file():
            raise FileNotFoundError(f"Input file not found: {self.filepath}")

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {self.filepath}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading file {self.filepath}: {e}")


        if not isinstance(data, dict):
             raise ValueError(f"YAML content in {self.filepath} is not a dictionary (key-value map).")

        print(f"    Successfully parsed YAML file: {self.filepath}")
        self._validate_data(data)
        print("    Input data validated.")
        return data

    def _validate_data(self, data: dict):
        """Performs validation checks on the loaded data."""
        # 1. Check for required keys
        missing_keys = [key for key in self.REQUIRED_KEYS if key not in data or not data[key]]
        if missing_keys:
            raise ValueError(f"Missing required keys in {self.filepath}: {', '.join(missing_keys)}")

        # 2. Check if list keys are actually lists (if they exist)
        for key in self.LIST_KEYS:
            if key in data and data[key] is not None and not isinstance(data[key], list):
                 # Allow None or empty lists, but raise error if it exists and is not a list
                 raise ValueError(f"Key '{key}' in {self.filepath} should be a list (e.g., using '- item'), but found type {type(data[key])}.")

        # 3. Check if path keys correspond to existing files (optional but helpful)
        #    We assume paths are relative to the project root (where the script runs)
        #    or absolute.
        project_root = Path.cwd() # Get the current working directory (project root)
        for key in self.PATH_KEYS:
            if key in data and data[key]:
                file_path_str = data[key]
                # Create a Path object. If it's absolute, it stays absolute.
                # If it's relative, resolve it relative to the project root.
                file_path = Path(file_path_str)
                if not file_path.is_absolute():
                    file_path = (project_root / file_path).resolve() # Check relative to CWD

                # Check if the resolved path actually exists as a file
                # Disabled check for now as logo might not exist yet
                # if not file_path.is_file():
                #    print(f"    Warning: File path specified for '{key}' does not seem to exist or is not a file: {file_path_str} (Resolved to: {file_path})")
                    # Depending on strictness, could raise ValueError here instead of printing warning

        # Add more specific checks as needed (e.g., roll number format)
        print("    Basic validation checks passed.")

# Example usage (if run directly for testing)
if __name__ == '__main__':
    # Assume project_data.yaml is in the parent directory when running this script directly
    # Adjust the path accordingly based on your test setup
    test_file_path = '../project_data.yaml'
    print(f"Testing InputParser with: {test_file_path}")
    try:
        parser = InputParser(test_file_path)
        project_data = parser.load_and_validate()
        print("\n--- Loaded Project Data ---")
        # Pretty print the dictionary
        import json
        print(json.dumps(project_data, indent=2))
        print("\n--- Test Successful ---")
    except (FileNotFoundError, yaml.YAMLError, ValueError, RuntimeError) as e:
        print(f"\n--- Test Failed ---")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n--- Test Failed ---")
        print(f"An unexpected error occurred: {e}")