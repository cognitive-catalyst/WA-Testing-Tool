#!/usr/bin/env python3
"""
Main CLI entry point for wxa-analyze.

This module provides a unified command-line interface for all analysis commands.
"""

import sys
from argparse import ArgumentParser


def main():
    """Main entry point for the wxa-analyze CLI."""
    parser = ArgumentParser(
        prog="python -m cli",
        description="Analyze and search various aspects of a watsonx Assistant instance",
        epilog="Use 'python -m cli.<command> --help' for more information on a specific command."
    )
    
    subparsers = parser.add_subparsers(
        title="Available commands",
        dest="command",
        help="Command to run",
        required=True,
        metavar="<command>"
    )
    
    # Define all available commands
    commands = {
        "action_metadata": {
            "module": "cli.action_metadata",
            "help": "Extract metadata for all actions in the assistant"
        },
        "assistant_metadata": {
            "module": "cli.assistant_metadata",
            "help": "Extract comprehensive metadata about the assistant"
        },
        "condition_usage": {
            "module": "cli.condition_usage",
            "help": "Report all conditions used in action steps"
        },
        "context_usage": {
            "module": "cli.context_usage",
            "help": "Report all context statements used in action steps"
        },
        "customer_response_settings": {
            "module": "cli.customer_response_settings",
            "help": "Extract customer response settings for action steps"
        },
        "entity_metadata": {
            "module": "cli.entity_metadata",
            "help": "Extract metadata for all entities defined in the assistant"
        },
        "entity_usage": {
            "module": "cli.entity_usage",
            "help": "Find where entities are used throughout the assistant"
        },
        "extension_usage": {
            "module": "cli.extension_usage",
            "help": "Find all custom extension calls in the assistant"
        },
        "intent_usage": {
            "module": "cli.intent_usage",
            "help": "Find where intents are used in action conditions and step handlers"
        },
        "response_usage": {
            "module": "cli.response_usage",
            "help": "Report all customer response types used in action steps"
        },
        "step_summary": {
            "module": "cli.step_summary",
            "help": "Get a comprehensive summary of each step for specified actions"
        },
        "subaction-usage": {
            "module": "cli.subaction_usage",
            "help": "Find all subaction invocations in the assistant"
        },
        "validation_settings": {
            "module": "cli.validation_settings",
            "help": "Extract validation settings for action steps"
        },
        "variable_metadata": {
            "module": "cli.variable_metadata",
            "help": "Extract metadata for all variables defined in the assistant"
        },
        "variable_usage": {
            "module": "cli.variable_usage",
            "help": "Find where variables are used throughout the assistant"
        },
    }
    
    # Add subparsers for each command
    for cmd_name, cmd_info in commands.items():
        subparsers.add_parser(
            cmd_name,
            help=cmd_info["help"],
            add_help=False  # Let the actual module handle help
        )
    
    # Parse only the command name first
    args, remaining = parser.parse_known_args()
    
    # Get the module for the selected command
    if args.command in commands:
        module_name = commands[args.command]["module"]
        
        # Import and run the command's main function
        try:
            # Restore sys.argv to include the remaining arguments
            sys.argv = [f"python -m cli.{args.command.replace('-', '_')}"] + remaining
            
            # Import the module dynamically
            import importlib
            module = importlib.import_module(module_name)
            
            # Run the main function
            module.main()
        except ImportError as e:
            print(f"Error: Could not import module '{module_name}': {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error running command '{args.command}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
