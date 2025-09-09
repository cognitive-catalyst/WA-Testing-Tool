from argparse import ArgumentParser
from dotenv import load_dotenv

from config.config import get_config
from src.utils.clean_cli_list import clean_cli_list
from src.utils.file_path_helper import get_assistant_json, create_directory, get_output_save_path
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main():
    cfg = get_config()
    
    parser = ArgumentParser(description="Search for subaction usage inside an assistant")
    # TODO: There is currently no good way to search for extensions because the assistant JSON doesn't include their name
    parser.add_argument('extensions', nargs='*', help='List of extensions names to search for.')
    parser.add_argument('-i', '--assistant_json_path', required=False, default=cfg["assistant_json_directory"], type=str, help=f'Path to assistant json. If not included, the code will search for one in `{cfg["assistant_json_directory"]}`.')
    parser.add_argument('-o', '--output_path', required=False, default=cfg["output_directory"], type=str, help=f'Path to output directory where the results will be saved. If not included, the code default to `{cfg["output_directory"]}`.')
    args = parser.parse_args()

    assistant_obj = get_assistant_json(args.assistant_json_path)
    analyzer = AssistantStaticAnalyzer(assistant_obj)

    extensions = clean_cli_list(args.extensions)
    if len(extensions):
        extension_usage_df = analyzer.search_for_extensions(*extensions, return_as="csv")
        default_file_name = f"{', '.join(extensions)} usage.csv"
    else:
        extension_usage_df = analyzer.get_all_extension_usage(return_as="csv")
        default_file_name = f"all extension usage.csv"
    
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    extension_usage_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()