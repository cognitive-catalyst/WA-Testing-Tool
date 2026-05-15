from argparse import ArgumentParser, RawDescriptionHelpFormatter

from config.config import get_config
from src.analyzers import IntentAnalyzer
from src.models.assistant import Assistant

from .utils.clean_cli_list import clean_cli_list
from .utils.file_path_helper import (
    create_directory,
    get_assistant_json,
    get_output_save_path,
)


def main():
    cfg = get_config()
    
    parser = ArgumentParser(
        description="Find where intents are used in action conditions and step handlers",
        epilog="Examples:\n"
               "  python -m cli.intent_usage                    # All actions\n"
               "  python -m cli.intent_usage action_1           # Single action\n"
               "  python -m cli.intent_usage action_1 action_2  # Multiple actions",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'action_ids',
        nargs='*',
        metavar='ACTION_ID',
        help='One or more action IDs to analyze. If omitted, analyzes all actions in the assistant.'
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
    intent_analyzer = IntentAnalyzer(assistant)

    action_ids = clean_cli_list(args.action_ids)
    intent_usage_df = intent_analyzer.intent_usage(*action_ids, return_as="dataframe")

    default_file_name = "all_intent_usage.csv"
    if len(action_ids):
        default_file_name = f"intent_usage ({', '.join(action_ids)}).csv"

    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    intent_usage_df.to_csv(output_path, index=False)
    
    print(f"Intent usage saved to: {output_path}")

if __name__ == "__main__":
    main()
