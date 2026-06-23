from argparse import ArgumentParser

from config.config import get_config
from src.analyzers import ActionAnalyzer
from src.models.assistant import Assistant
from src.output_handlers import OutputFormat

from .utils.file_path_helper import (
    create_directory,
    get_assistant_json,
    get_output_save_path,
)


def main():
    cfg = get_config()
    
    parser = ArgumentParser(
        description="Extract metadata for all actions in the assistant",
        epilog="Example: python -m cli.action_metadata -i assistant.json -o ./reports"
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
        help=f'Directory where the CSV output will be saved. Default: {cfg["output_directory"]}'
    )
    args = parser.parse_args()

    assistant_dict = get_assistant_json(args.assistant_json_path)
    assistant = Assistant.from_dict(assistant_dict)
    action_analyzer = ActionAnalyzer(assistant)
    
    action_metadata_df = action_analyzer.action_metadata(return_as=OutputFormat.DATAFRAME)

    action_metadata_df = action_metadata_df.sort_values("action_id")

    default_file_name = "action_metadata.csv"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    action_metadata_df.to_csv(output_path, index=False)
    
    print(f"Action metadata saved to: {output_path}")

if __name__ == "__main__":
    main()
