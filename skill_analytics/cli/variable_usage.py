from argparse import ArgumentParser, RawDescriptionHelpFormatter

from config.config import get_config
from src.analyzers import VariableAnalyzer
from src.models.assistant import Assistant
from src.output_handlers import OutputFormat

from .utils.clean_cli_list import clean_cli_list
from .utils.file_path_helper import (
    create_directory,
    get_assistant_json,
    get_output_save_path,
)


def main():
    cfg = get_config()
    
    parser = ArgumentParser(
        description="Find where variables are used throughout the assistant",
        epilog="Examples:\n"
               "  python -m cli.variable_usage                        # All variables\n"
               "  python -m cli.variable_usage var1                   # Single variable\n"
               "  python -m cli.variable_usage var1 var2              # Multiple variables\n"
               "  python -m cli.variable_usage --metadata             # Include variable metadata",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'variables',
        nargs='*',
        metavar='VARIABLE_NAME',
        help='One or more variable names to search for. If omitted, reports usage of all variables.'
    )
    parser.add_argument(
        '--metadata',
        action='store_true',
        default=False,
        help='Include variable metadata (type, scope, initial values) in the output.'
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
    variable_analyzer = VariableAnalyzer(assistant)

    variable_ids = clean_cli_list(args.variables)
    variable_usage_df = variable_analyzer.get_variable_usage(*variable_ids, return_as=OutputFormat.DATAFRAME)

    if args.metadata:
        variable_metadata_df = variable_analyzer.get_variable_metadata(return_as=OutputFormat.DATAFRAME)
        
        # Drop columns that would conflict or are redundant
        variable_metadata_df = variable_metadata_df.drop(columns=['id', 'action_id', 'step_id', 'type'])

        # Prepend 'variable_' to all columns in variable_summary_df
        variable_metadata_df = variable_metadata_df.add_prefix('variable_')
        
        # Join on uid = variable_uid
        variable_usage_df = variable_usage_df.merge(
            variable_metadata_df,
            left_on='variable_uid',
            right_on='variable_uid',
            how='left'
        )

    default_file_name = "all_variable_usage.csv"
    if len(variable_ids):
        default_file_name = f"variable_usage ({', '.join(variable_ids)}).csv"

    # variable_usage_df = move_col_to_front(variable_usage_df, "variable")
    
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    variable_usage_df.to_csv(output_path, index=False)
    
    print(f"Variable usage saved to: {output_path}")

if __name__ == "__main__":
    main()