from argparse import ArgumentParser
from dotenv import load_dotenv

from config.config import get_config
from src.utils.file_path_helper import get_assistant_json, create_directory, get_output_save_path
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main():
    cfg = get_config()
    
    parser = ArgumentParser(description="Summary of all variables defined in the assistant")
    parser.add_argument('-s', '--system_variables', action='store_true', default=False, help="If included, the output will include system variables.")
    parser.add_argument('-a', '--action_variables', action='store_true', default=False, help="If included, the output will include action variables.")
    parser.add_argument('-i', '--assistant_json_path', required=False, default=cfg["assistant_json_directory"], type=str, help=f'Path to assistant json. If not included, the code will search for one in `{cfg["assistant_json_directory"]}`.')
    parser.add_argument('-o', '--output_path', required=False, default=cfg["output_directory"], type=str, help=f'Path to output directory where the results will be saved. If not included, the code default to `{cfg["output_directory"]}`.')
    args = parser.parse_args()

    assistant_obj = get_assistant_json(args.assistant_json_path)
    analyzer = AssistantStaticAnalyzer(assistant_obj)

    variable_summary_df = analyzer.variable_summary(return_as="csv")
    
    all_false = not any([args.system_variables, args.action_variables])
    if not args.system_variables and not all_false:
        variable_summary_df = variable_summary_df[variable_summary_df["source"] != "system_variable"]
    if not args.action_variables and not all_false:
        variable_summary_df = variable_summary_df[variable_summary_df["source"] != "action_variable"]

    variable_summary_df = variable_summary_df.sort_values("variable_id")
    if 'step_number' in variable_summary_df.columns:
        variable_summary_df['step_number'] = variable_summary_df['step_number'].astype('Int64')

    default_file_name = "variable_summary.csv"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    variable_summary_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()