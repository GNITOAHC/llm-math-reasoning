import argparse
from openai_reasoning.main import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Reasoning for math problems")
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-l", "--log", type=str, required=True)
    parser.add_argument("-r", "--reasoning", type=str, required=False)
    args = parser.parse_args()
    run(args.input, args.log, args.reasoning)
