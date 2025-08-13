import argparse

from pure_reasoning.main import run as run_pure_reasoning
from tool_assisted.main import run as run_tool_assisted


def main():
    parser = argparse.ArgumentParser(description="LLM Reasoning for math problems")

    # Shared flags container
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument("-i", "--input", type=str, required=True)
    shared_parser.add_argument("-l", "--log", type=str, required=True)
    shared_parser.add_argument("-r", "--reasoning", type=str, required=False)

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: "pure-reasoning"
    pure_reasoning_parser = subparsers.add_parser(
        "pure-reasoning", parents=[shared_parser]
    )

    # Subcommand: "tool-assisted"
    tool_assisted_parser = subparsers.add_parser(
        "tool-assisted", parents=[shared_parser]
    )

    args = parser.parse_args()

    # Handle commands
    match args.command:
        case "pure-reasoning":
            run_pure_reasoning(args.input, args.log, args.reasoning)
        case "tool-assisted":
            run_tool_assisted(args.input, args.log, args.reasoning)


if __name__ == "__main__":
    main()
