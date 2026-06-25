from argparse import ArgumentParser, RawDescriptionHelpFormatter

from config.config import get_config
from src.analyzers import VariableAnalyzer
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
        description="Extract metadata for all variables defined in the assistant",
        epilog="Examples:\n"
               "  python -m cli.variable_metadata                      # All variable types\n"
               "  python -m cli.variable_metadata --skill_variables    # Only skill variables\n"
               "  python -m cli.variable_metadata --step_variables --result_variables  # Multiple types",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--skill_variables',
        action='store_true',
        default=False,
        help='Include only skill (action-level) variables. If no flags are set, all types are included.'
    )
    parser.add_argument(
        '--step_variables',
        action='store_true',
        default=False,
        help='Include only step (local) variables. If no flags are set, all types are included.'
    )
    parser.add_argument(
        '--result_variables',
        action='store_true',
        default=False,
        help='Include only result variables from extensions/subactions. If no flags are set, all types are included.'
    )
    parser.add_argument(
        '--system_variables',
        action='store_true',
        default=False,
        help='Include only system variables (built-in Watson variables). If no flags are set, all types are included.'
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
    
    all_false = not any([args.skill_variables, args.step_variables, args.result_variables, args.system_variables])
    if all_false:
        variable_metadata_df = variable_analyzer.get_variable_metadata(return_as=OutputFormat.DATAFRAME)
    else:
        variable_metadata_df = variable_analyzer.get_variable_metadata(
            include_skill_variables=args.skill_variables,
            include_step_variables=args.step_variables,
            include_result_variables=args.result_variables,
            include_system_variables=args.system_variables,
            return_as=OutputFormat.DATAFRAME,
        )

    variable_metadata_df = variable_metadata_df.sort_values("id")
    # if 'step_number' in variable_metadata_df.columns:
    #     variable_metadata_df['step_number'] = variable_metadata_df['step_number'].astype('Int64')

    default_file_name = "variable_metadata.csv"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    variable_metadata_df.to_csv(output_path, index=False)
    
    print(f"Variable metadata saved to: {output_path}")

if __name__ == "__main__":
    main()