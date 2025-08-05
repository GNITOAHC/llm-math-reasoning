import os
import io
import re
import json
import time

import dotenv
import traceback 
from contextlib import redirect_stdout, redirect_stderr  
from pure_reasoning.reasoning_model import OpenAIReasoning
from tool_assisted.prompts import CODE_GENERATOR_PROMPT, FIX_CODE_PROMPT
from general_prompts import prompts

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


def run_generated_code(code_str: str) -> str:
    """
    Execute LLM-generated python code safely, capture stdout/stderr,
    and make sure required modules (e.g., pulp) are visible.
    Returns the combined stdout/stderr text.
    """
    # Normalize NBSP and similar unicode spaces
    cleaned = code_str.replace('\u00A0', ' ')
    
    # Prepare execution namespace
    env = {"__name__": "__main__"}  # [MOD]
    try:
        import pulp  # noqa
        env["pulp"] = pulp
    except Exception:
        pass  # If pulp isn't installed, let the code raise a clear error
    
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    
    try:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            exec(cleaned, env, env)
    except Exception:
        out_buf.write("---------- TRACEBACK ----------\n")
        out_buf.write(traceback.format_exc())
        out_buf.write("---------- END TRACEBACK ------\n")
    
    # Merge outputs
    stderr_text = err_buf.getvalue()
    if stderr_text:
        out_buf.write("\n[STDERR]\n")
        out_buf.write(stderr_text)
    
    return out_buf.getvalue()


def _has_objective(text: str) -> bool:
    if not isinstance(text, str):
        return False
    pattern = r"Objective value:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
    return re.search(pattern, text) is not None


def _is_error_output(text: str) -> bool:
    if not isinstance(text, str):
        return True
    err_keywords = (
        "Traceback",
        "DATA_VALIDATION_FAILED",
        "RuntimeError",
        "AssertionError",
        "Matrix must be n x n",
        "not symmetric",
        "length",
    )
    return any(k in text for k in err_keywords)


# for IO errors
def _extract_code_from_markdown(s: str) -> str:
    try:
        if "```python" in s:
            return s.split("```python", 1)[1].split("```", 1)[0]
        if "```" in s:
            # generic fence fallback
            return s.split("```", 1)[1].split("```", 1)[0]
    except Exception:
        pass
    return s


def _violates_io(code: str) -> bool:
    if not isinstance(code, str):
        return True
    lowered = code.lower()
    banned = (
        "with open(", "open(", "csv.", "pd.read", "pandas", "read_csv",
        "urllib", "requests", "http://", "https://", "pathlib", "glob.glob",
        "sqlite3", "psycopg2", "boto3", "json.load(", "yaml.safe_load(",
        "argparse", "sys.argv", "np.random", "random.", "torch.", "sklearn."
    )
    return any(tok in lowered for tok in banned)


def _missing_required_context(code: str) -> bool:
    if not isinstance(code, str):
        return True
    need = ("raw_problem_text", "raw_model_text", "raw_classification_json")
    return not all(k in code for k in need)


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


    # Step 5: Generate code 
    gen_code = model.complete(
        "",
        system_prompt=CODE_GENERATOR_PROMPT.format(
            MATH_MODEL=modified_answer
        )
    ) 
    code_result = gen_code.strip()
    print("\nGenerated Code:\n", code_result)


    # Step 6: Extract code 
    problem = problem_description
    final_answer = modified_answer
    classification_json_str = json.dumps({"classification": classification_response})

    # Extract python
    if "```python" in code_result:
        final_code = code_result.split("```python", 1)[1].split("```", 1)[0]
    elif "```" in code_result:
        final_code = code_result.split("```", 1)[1].split("```", 1)[0]
    else:
        final_code = code_result
    print(f"Extracted Code (initial):\n{final_code}\n")

    # Guard: forbid external I/O and enforce embedded raw context
    if _violates_io(final_code) or _missing_required_context(final_code):
        fix_mes = (
            "Detected forbidden external I/O or missing required embedded raw strings. "
            "Remove all external reads and ensure raw_problem_text/raw_model_text/raw_classification_json are present."
        )
        F_FIX_CODE_PROMPT = FIX_CODE_PROMPT.format(
            code=final_code,
            raw_problem=problem,
            raw_model=final_answer,
            classification_json=classification_json_str,
        )
        fixed_code = model.complete(
            fix_mes,
            system_prompt=F_FIX_CODE_PROMPT,
        )
        fixed_code = _extract_code_from_markdown(fixed_code) if "```" in fixed_code else fixed_code
        if fixed_code.strip() == "":
            fixed_code = fixed_code

    exec_output = run_generated_code(fixed_code)
    print(exec_output)


    # Step 7: Auto debug
    max_auto_fixes = 3
    attempt = 0
    while (not _has_objective(exec_output) or _is_error_output(exec_output)) and attempt < max_auto_fixes:
        attempt += 1
        print(f"[Auto-Debug] Attempt {attempt}: objective missing or error detected. Re‑invoking FIX_CODE_PROMPT…")

        F_FIX_CODE_PROMPT = FIX_CODE_PROMPT.format(
            code=final_code,
            raw_problem=problem,
            raw_model=final_answer,
            classification_json=classification_json_str,
        )
        fix_mes = (
            "Runtime error / logs from previous run:\n" + exec_output +
            "\n\nPlease fix the Python code so it runs successfully, embeds the three raw strings, performs no external I/O, "
            "and outputs a line of the exact form 'Objective value: <number>'. Return ONLY the corrected Python code in a fenced block."
        )

        # Ask the model to fix the code using the error logs; then extract the corrected code
        math_ans = model.complete(
            fix_mes,
            system_prompt=F_FIX_CODE_PROMPT,
        )

        # Extract corrected code from markdown fences (if present)
        if "```python" in math_ans:
            final_code = math_ans.split("```python", 1)[1].split("```", 1)[0]
        elif "```" in math_ans:
            final_code = math_ans.split("```", 1)[1].split("```", 1)[0]
        else:
            final_code = math_ans
        print(f"[Auto-Debug] attempt {attempt}).")

        # Re-execute with the corrected code
        exec_output = run_generated_code(final_code)
        print(exec_output)

    # Final result text returned from solve()
    final_answer = exec_output

    END_TIME = time.time()
    TIME_USED = END_TIME - START_TIME

    # Step 8: Extract the final answer's number and compare it with the answer
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
