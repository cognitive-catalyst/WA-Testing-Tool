from argparse import ArgumentParser
from dotenv import load_dotenv

from config.config import get_config
from src.utils.clean_cli_list import clean_cli_list
from src.utils.file_path_helper import get_assistant_json, create_directory, get_output_save_path
from src.utils.dataframe_helper import move_col_to_front
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main():
    cfg = get_config()
    
    parser = ArgumentParser(description="Search for entity usage inside an assistant")
    parser.add_argument('entities', nargs='*', help='List of entity names to search for.')
    parser.add_argument('-d', '--definition_only', action='store_true', default=False, help="If included, the output will include the places where the entity was defined, not where it was used.")
    parser.add_argument('-i', '--assistant_json_path', required=False, default=cfg["assistant_json_directory"], type=str, help=f'Path to assistant json. If not included, the code will search for one in `{cfg["assistant_json_directory"]}`.')
    parser.add_argument('-o', '--output_path', required=False, default=cfg["output_directory"], type=str, help=f'Path to output directory where the results will be saved. If not included, the code default to `{cfg["output_directory"]}`.')
    args = parser.parse_args()

    assistant_obj = get_assistant_json(args.assistant_json_path)
    analyzer = AssistantStaticAnalyzer(assistant_obj)

    entities = clean_cli_list(args.entities)
    if len(entities):
        entity_usage_df = analyzer.search_for_entities(*entities, return_as="csv")
        default_file_name = f"{', '.join(entities)} usage.csv"
    else:
        entity_usage_df = analyzer.get_all_entity_usage(return_as="csv")
        default_file_name = "all entity usage.csv"
    
    if args.definition_only:
        entity_usage_df = entity_usage_df[entity_usage_df["source"] == "customer_response"]

    entity_usage_df = move_col_to_front(entity_usage_df, "entity")
    entity_usage_df = entity_usage_df.dropna(axis=1, how='all')

    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    entity_usage_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()