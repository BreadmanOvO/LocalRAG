import os

def get_project_root() -> str:
    """Returns the absolute path to the project root directory."""
    current_file_path = os.path.abspath(__file__)
    current_dir_path = os.path.dirname(current_file_path)
    project_root = os.path.dirname(current_dir_path)
    return project_root

def get_abs_path(relative_path: str) -> str:
    """Converts a relative path to an absolute path based on the project root."""
    project_root = get_project_root()
    abs_path = os.path.join(project_root, relative_path)
    return abs_path
