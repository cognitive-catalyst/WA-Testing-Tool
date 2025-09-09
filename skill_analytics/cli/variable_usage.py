from argparse import ArgumentParser
from dotenv import load_dotenv

from config.config import get_config
from src.utils.clean_cli_list import clean_cli_list
from src.utils.file_path_helper import get_assistant_json, create_directory, get_output_save_path
from src.utils.dataframe_helper import move_col_to_front
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main():
    cfg = get_config()
    
    parser = ArgumentParser(description="Search for variable usage inside an assistant")
    parser.add_argument('variables', nargs='*', help='List of variable names to search for.')
    parser.add_argument('-i', '--assistant_json_path', required=False, default=cfg["assistant_json_directory"], type=str, help=f'Path to assistant json. If not included, the code will search for one in `{cfg["assistant_json_directory"]}`.')
    parser.add_argument('-o', '--output_path', required=False, default=cfg["output_directory"], type=str, help=f'Path to output directory where the results will be saved. If not included, the code default to `{cfg["output_directory"]}`.')
    args = parser.parse_args()

    assistant_obj = get_assistant_json(args.assistant_json_path)
    analyzer = AssistantStaticAnalyzer(assistant_obj)

    variables = clean_cli_list(args.variables)
    if len(variables):
        variable_usage_df = analyzer.search_for_variables(*variables, return_as="csv")
        default_file_name = f"{', '.join(variables)} usage.csv"
    else:
        variable_usage_df = analyzer.get_all_variable_usage(return_as="csv")
        default_file_name = "all variable usage.csv"
    
    variable_usage_df = move_col_to_front(variable_usage_df, "variable")

    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    variable_usage_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()