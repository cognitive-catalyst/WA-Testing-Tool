import json
from argparse import ArgumentParser

from config.config import get_config
from src.analyzers import AssistantAnalyzer
from src.models.assistant import Assistant

from .utils.file_path_helper import (
    create_directory,
    get_assistant_json,
    get_output_save_path,
)


def main():
    cfg = get_config()
    
    parser = ArgumentParser(
        description="Extract comprehensive metadata about the assistant including IDs, settings, and aggregated statistics",
        epilog="Example: python -m cli.assistant_metadata -i assistant.json -o ./reports"
    )
    parser.add_argument(
        '-i', '--assistant_json_path',
        required=False,
        default=cfg["assistant_json_directory"],
        type=str,
        metavar='PATH',
        help=f'Path to the watsonx Assistant JSON file. Default: {cfg["assistant_json_directory"]}'
    )
    parser.add_argument(
        '-o', '--output_path',
        required=False,
        default=cfg["output_directory"],
        type=str,
        metavar='PATH',
        help=f'Directory where the JSON output will be saved. Default: {cfg["output_directory"]}'
    )
    args = parser.parse_args()

    assistant_dict = get_assistant_json(args.assistant_json_path)
    assistant = Assistant.from_dict(assistant_dict)
    assistant_analyzer = AssistantAnalyzer(assistant)
    
    # Get metadata as Python dict (list with single dict)
    assistant_metadata = assistant_analyzer.assistant_metadata(return_as="python")
    
    # Since there's only one assistant, extract the single dict from the list
    metadata_dict = assistant_metadata[0] if assistant_metadata else {}

    default_file_name = "assistant_metadata.json"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    
    # Write as formatted JSON
    with open(output_path, 'w') as f:
        json.dump(metadata_dict, f, indent=2)
    
    print(f"Assistant metadata saved to: {output_path}")

if __name__ == "__main__":
    main()
