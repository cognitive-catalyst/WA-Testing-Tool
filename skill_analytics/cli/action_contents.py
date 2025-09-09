from argparse import ArgumentParser
from dotenv import load_dotenv
import pandas as pd

from config.config import get_config
from src.utils.clean_cli_list import clean_cli_list
from src.utils.file_path_helper import get_assistant_json, create_directory, get_output_save_path
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main():
    cfg = get_config()
    
    parser = ArgumentParser(description="Search for action contents inside an assistant")
    parser.add_argument('actions', nargs='*', help='List of actions names to search contents of.')
    parser.add_argument('-v', '--variables', action='store_true', default=False, help="If included, the output will include all variable usage inside the listed actions.")
    parser.add_argument('-s', '--subactions', action='store_true', default=False, help="If included, the output will include all subaction usage inside the listed actions.")
    parser.add_argument('-e', '--extensions', action='store_true', default=False, help="If included, the output will include all extension usage inside the listed actions.")
    parser.add_argument('-r', '--responses', action='store_true', default=False, help="If included, the output will include all text response inside the listed actions.")
    parser.add_argument('-i', '--assistant_json_path', required=False, default=cfg["assistant_json_directory"], type=str, help=f'Path to assistant json. If not included, the code will search for one in `{cfg["assistant_json_directory"]}`.')
    parser.add_argument('-o', '--output_path', required=False, default=cfg["output_directory"], type=str, help=f'Path to output directory where the results will be saved. If not included, the code default to `{cfg["output_directory"]}`.')
    args = parser.parse_args()

    content_types = {
        "variables": args.variables,
        "subactions": args.subactions,
        "extensions": args.extensions,
        "responses": args.responses,
    }

    assistant_obj = get_assistant_json(args.assistant_json_path)
    analyzer = AssistantStaticAnalyzer(assistant_obj)

    actions = clean_cli_list(args.actions)
    action_contents_df = pd.DataFrame()
    all_false = not any(content_types.values())
    
    if args.variables or all_false:
        variable_usage_df = analyzer.get_all_variables_used_in_action(*actions, return_as="csv")
        action_contents_df = pd.concat([action_contents_df, variable_usage_df], ignore_index=True)
    
    if args.subactions or all_false:
        subaction_usage_df = analyzer.get_all_subactions_used_in_action(*actions, return_as="csv")
        action_contents_df = pd.concat([action_contents_df, subaction_usage_df], ignore_index=True)
    
    if args.extensions or all_false:
        extension_usage_df = analyzer.get_all_extensions_used_in_action(*actions, return_as="csv")
        action_contents_df = pd.concat([action_contents_df, extension_usage_df], ignore_index=True)
    
    if args.responses or all_false:
        responses_df = analyzer.get_all_responses_in_action(*actions, return_as="csv")
        action_contents_df = pd.concat([action_contents_df, responses_df], ignore_index=True)
    
    contents_string = "all contents" if all_false else ', '.join([content_name for content_name, content_included in content_types.items() if content_included])
    default_file_name = f"{', '.join(actions)} - {contents_string}.csv" if actions else f"all actions - {contents_string}.csv"
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    action_contents_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()