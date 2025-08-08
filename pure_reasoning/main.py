import os
import json
import time

import dotenv

from pure_reasoning.reasoning_model import OpenAIReasoning
from pure_reasoning.prompts import FINAL_ANSWER_PROMPT
from general_prompts import prompts


dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


def run(input_path: str, log_file_path: str, reasoning):
    # Read the problem description from the input file
    with open(input_path, "r") as f:
        problem_description = f.read()

    # Instantiate the reasoning model
    model = OpenAIReasoning(api_key=OPENAI_API_KEY, model="o3")

    if reasoning:
        model.reasoning_effort = reasoning

    START_TIME = time.time()

    # Step 1: Classify the problem
    classification_response = model.complete(
        problem_description, system_prompt=prompts.PROBLEM_MATCHING_PROMPT
    )
    print("Classification:\n", classification_response)

    # Step 2: Generate initial answer
    initial_answer = model.complete(
        problem_description,
        system_prompt=prompts.INIT_ANSWER_PROMPT.format(
            detected_type=classification_response, complexity="simple"
        ),
    )
    print("\nInitial Answer:\n", initial_answer)

    # Step 3: Expert review
    expert_review = model.complete(
        initial_answer,
        system_prompt=prompts.GENERAL_EXPERT_PROMPT.format(
            original_problem_text=problem_description,
            detected_type=classification_response,
            complexity="simple",
        ),
    )
    print("\nExpert Review:\n", expert_review)

    # Step 4: Generate modified answer based on review
    modified_answer = model.complete(
        "",
        system_prompt=prompts.MODIFIED_INIT_ANSWER_PROMPT.format(
            INIT_ANSWER=initial_answer, REVIEW=expert_review
        ),
    )
    print("\nModified Answer:\n", modified_answer)

    # Step 5: Get the final answer by reasoning
    final_answer = model.complete(
        f"Problem Description:\n{problem_description}\n\nMathematical Formulation:\n{modified_answer}",
        system_prompt=FINAL_ANSWER_PROMPT,
    )
    print("\nFinal Answer:\n", final_answer)

    END_TIME = time.time()
    TIME_USED = END_TIME - START_TIME

    # Step 6: Extract the final answer's number and compare it with the answer
    ans_path = input_path
    ans_path = ans_path.replace("desc", "ans")
    with open(ans_path, "r") as f:
        answer = f.read()

    print("\nAnswer:\n", answer)

    check_answer_model = OpenAIReasoning(api_key=OPENAI_API_KEY, model="o3-mini")
    check_answer = check_answer_model.complete(
        f"Following is the final answer to a specific problem, please extract the number from it.\n\nAnswer: {final_answer},\n\nMoreover, this is the correct answer to this problem: {answer}. Please tell me if they are same. If they are same, please output `correct; {{the extracted answer}}; {{the correct answer}}`, else, please output `incorrect; {{the extracted answer}}; {{the correct answer}}`",
        system_prompt="You are a helpful assistant that helps extract the final answer(mostly number) from a answer to a specific problem",
    )
    print("\nCheck Answer:\n", check_answer)

    parsed_check_answer = check_answer.split("; ")
    try:
        correct: bool = parsed_check_answer[0] == "correct"
        llm_answer = parsed_check_answer[1]
        correct_answer = parsed_check_answer[2]
    except:
        correct: bool = False
        llm_answer = ""
        correct_answer = ""

    # Append output to specified log file
    with open(log_file_path, "w") as f:
        log_json = {
            "input_question": input_path,
            "raw_final_answer": check_answer,
            "correct": correct,
            "llm_answer": llm_answer,
            "correct_answer": correct_answer,
            "token_usage": model.token_used(),
            "time_used": TIME_USED,
        }
        f.write(json.dumps(log_json))
        f.write("\n")
