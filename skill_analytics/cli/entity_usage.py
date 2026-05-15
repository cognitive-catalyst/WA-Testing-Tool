from argparse import ArgumentParser, RawDescriptionHelpFormatter

from config.config import get_config
from src.analyzers import EntityAnalyzer
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
        description="Find where entities are used throughout the assistant",
        epilog="Examples:\n"
               "  python -m cli.entity_usage                      # All entities\n"
               "  python -m cli.entity_usage sys-date             # Single entity\n"
               "  python -m cli.entity_usage sys-date sys-time    # Multiple entities\n"
               "  python -m cli.entity_usage --metadata           # Include entity metadata",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'entities',
        nargs='*',
        metavar='ENTITY_ID',
        help='One or more entity IDs to search for. If omitted, reports usage of all entities.'
    )
    parser.add_argument(
        '--metadata',
        action='store_true',
        default=False,
        help='Include entity metadata (type, values, fuzzy matching settings) in the output.'
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
    entity_analyzer = EntityAnalyzer(assistant)

    entity_ids = clean_cli_list(args.entities)
    entity_usage_df = entity_analyzer.entity_usage(*entity_ids, return_as="dataframe")

    if args.metadata:
        entity_metadata_df = entity_analyzer.entity_metadata(return_as="dataframe")
        
        # Prepend 'entity_' to all columns in entity_metadata_df to avoid conflicts
        entity_metadata_df = entity_metadata_df.add_prefix('entity_metadata_')
        
        # Join on entity_id = entity_metadata_entity_id
        entity_usage_df = entity_usage_df.merge(
            entity_metadata_df,
            left_on='entity_id',
            right_on='entity_metadata_entity_id',
            how='left'
        )

    default_file_name = "all_entity_usage.csv"
    
    create_directory(args.output_path)
    output_path = get_output_save_path(args.output_path, default_file_name)
    entity_usage_df.to_csv(output_path, index=False)
    
    print(f"Entity usage saved to: {output_path}")

if __name__ == "__main__":
    main()
