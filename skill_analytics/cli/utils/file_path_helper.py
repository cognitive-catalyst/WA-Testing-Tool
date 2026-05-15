from pathlib import Path
import json

def get_json_file_from_directory(directory_path_str):
    directory_path = Path(directory_path_str)
    json_files = list(directory_path.glob('*.json'))
    json_file_paths = [str(file) for file in json_files]
    return json_file_paths

def load_json_file(json_file_path):
    return json.load(open(json_file_path, 'r'))

def create_directory(directory_path_str):
    directory_path = Path(directory_path_str)
    directory_path.mkdir(parents=True, exist_ok=True)

def get_output_save_path(path_str, default_file_name):

    path = Path(path_str)
    default_ext = Path(default_file_name).suffix.lower()

    if path.exists() and path.is_file():
        # Check if file extension matches
        if path.suffix.lower() == default_ext:
            return str(path)
        else:
            raise ValueError(f"File extension does not match: expected '{default_ext}', got '{path.suffix}'")

    elif path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        full_path = path / default_file_name
        return str(full_path)

    else:
        raise ValueError(f"Invalid path: {path_str}")

def get_assistant_json(path_str):
    path = Path(path_str)

    if path.is_file():
        if path.suffix.lower() != '.json':
            raise ValueError(f"Path '{path_str}' is not a path to a json file nor a directory containing a json file.")
        return load_json_file(str(path))
    
    elif path.is_dir():
        json_file_paths = get_json_file_from_directory(str(path))
        if len(json_file_paths) == 0:
            raise ValueError(f"Path '{path_str}' did not contain any json files.")
        if len(json_file_paths) > 1:
            raise ValueError(f"Path '{path_str}' contains many json files, please specify which one you want to analyze.")
        return load_json_file(json_file_paths[0])

    else:
        raise ValueError(f"Path '{path_str}' could not be found.")