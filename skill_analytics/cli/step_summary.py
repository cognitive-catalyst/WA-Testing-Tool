from argparse import ArgumentParser, RawDescriptionHelpFormatter

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
        description="Get a comprehensive summary of each step for specified actions",
        epilog="Examples:\n"
               "  python -m cli.step_summary                      # All actions\n"
               "  python -m cli.step_summary action_1             # Single action\n"
               "  python -m cli.step_summary action_1 action_2    # Multiple actions",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'action_ids',
        nargs='*',
        help='Optional action IDs to filter results. If not provided, analyzes all actions.'
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
    
    step_summary_df = action_analyzer.step_summary(*args.action_ids, return_as=OutputFormat.DATAFRAME)

    default_file_name = "step_summary.csv"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    step_summary_df.to_csv(output_path, index=False)
    
    print(f"Step summary saved to: {output_path}")

if __name__ == "__main__":
    main()
