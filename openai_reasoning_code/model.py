import os
import re
import io
import sys
import json
import argparse
import time  
from dotenv import load_dotenv
import traceback 
from contextlib import redirect_stdout, redirect_stderr  
from reasoning import OpenAIReasoning
from prompts import (PROBLEM_MATCHING_PROMPT, INIT_ANSWER_PROMPT, GENERAL_EXPERT_PROMPT, MODIFIED_INIT_ANSWER_PROMPT, 
                         CODE_GENERATOR_PROMPT, FIX_CODE_PROMPT, CHECK_MATCHING_PROMPT)


# RUN LONGER MAKE IT PRECISER
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = None  # will be initialised in main() once CLI args are parsed


""" 🌟 各問題呼叫路徑  

LP/ ILP 
DATASET_PATH = "datasets/dataset_LP/ILP/parsed_output"

TSP
DATASET_PATH = "datasets/dataset_tsp/parsed_output/small"
"""

DATASET_PATH = "datasets/dataset_Knapsack/small_100_1000"


def token_speed_calculator(step_name: str, token_log: dict, latest_tokens: dict, model: OpenAIReasoning, **kwargs) -> tuple[str, dict]:
    """
    一個輔助函式，用於呼叫模型、計時、計算 token 使用量與速度，並記錄日誌。
    
    Args:
        step_name (str): 當前步驟的名稱 (例如 "Classification")。
        token_log (dict): 要更新的日誌字典。
        latest_tokens (dict): 上一步驟結束後的 token 狀態。
        model (OpenAIReasoning): 模型實例。
        **kwargs: 要傳遞給 model.complete 的參數 (例如 mes, system_prompt)。

    Returns:
        tuple[str, dict]: API 的回傳結果和更新後的 token 狀態。
    """
    start_time = time.monotonic()
    
    result = model.complete(**kwargs)
    
    end_time = time.monotonic()
    duration = end_time - start_time
    
    # 計算 token 差異 (這就是您原有的欄位)
    current_tokens = model.token_used().copy()
    token_delta = {key: current_tokens[key] - latest_tokens.get(key, 0) for key in current_tokens}
    
    # 計算速度 (tokens per second)
    total_tokens_in_step = token_delta.get('total_tokens', 0)
    tokens_per_second = total_tokens_in_step / duration if duration > 0 else 0
    
    # 更新日誌，將原有 token 資訊和新的速度資訊都放進去
    token_log[step_name] = {
        "tokens_used": token_delta,
        "duration_seconds": round(duration, 4),
        "tokens_per_second": round(tokens_per_second, 2)
    }
    
    return result, current_tokens


# -----------------------------
# [MOD] Helper: safe code execution with captured stdout/stderr
# -----------------------------
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

# -----------------------------
# [MOD] Helpers: detect success/error and extract code
# -----------------------------
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


def solve(problem: str) -> tuple[str, dict]:

    token_log = {}
    latest_tokens = model.token_used().copy() 

    # --- CLASSIFICATION ---
    q_classify, latest_tokens = token_speed_calculator(
        "Classification", token_log, latest_tokens, model,
        mes=problem, system_prompt=PROBLEM_MATCHING_PROMPT
    )
    
    print("Classification Result:", q_classify, "\n")
    
    try:
        start = q_classify.find('{')
        end = q_classify.rfind('}') + 1
        q_c = json.loads(q_classify[start:end])
    except json.JSONDecodeError:
        print(f"CRITICAL ERROR: Initial classification failed. The model did not return valid JSON.")
        print(f"Content received: {q_classify}")
        raise
    
    detected_type = q_c.get("detected_type", "Unknown")
    
    print(f"Init Problem Type: {detected_type}", "\n")

    for i in range(5):
        F_CHECK_MATCHING_PROMPT = CHECK_MATCHING_PROMPT.format(
            detected_type=detected_type,
            math_model_text=q_classify,
        )
        q_classify, latest_tokens = token_speed_calculator(
            f"Check problem matching {i+1}", token_log, latest_tokens, model,
            mes=q_classify, system_prompt=F_CHECK_MATCHING_PROMPT
        )
    
    start = q_classify.find('{')
    end = q_classify.rfind('}') + 1   
    q_c = json.loads(q_classify[start:end])
    classification_json_str = json.dumps(q_c, ensure_ascii=False)

    COMPLEXITY_TABLE = {
        "LP": "P", "ILP": "NP-hard", "MILP": "NP-hard", "QP": "NP-hard",
        "NLP": "NP-hard", "Knapsack": "NP-complete", "TSP": "NP-complete",
        "Set Cover": "NP-complete", "GCP": "NP-hard", "Others": "Others"
    }
    complexity = COMPLEXITY_TABLE.get(q_c["detected_type"], "Unknown")

    print(f"Final Problem Type: {q_c['detected_type']}")
    print(f"Problem Complexity: {complexity}", "\n")

    # --- INITIAL ANSWER ---
    F_INIT_ANSWER_PROMPT = INIT_ANSWER_PROMPT.format(
        detected_type=q_c["detected_type"],
        complexity=complexity
    )
    init_answer, latest_tokens = token_speed_calculator(
        "Initial Answer", token_log, latest_tokens, model,
        mes=problem, system_prompt=F_INIT_ANSWER_PROMPT
    )

    print("Initial Answer:", init_answer, "\n")

    # --- REVIEW ---
    F_GENERAL_EXPERT_PROMPT = GENERAL_EXPERT_PROMPT.format(
        detected_type=q_c["detected_type"],
        complexity=complexity,
        original_problem_text=problem,
    )
    review_answer, latest_tokens = token_speed_calculator(
        "Review", token_log, latest_tokens, model,
        mes=init_answer, system_prompt=F_GENERAL_EXPERT_PROMPT
    )

    print("Review Answer:", review_answer, "\n")

    # --- REFINE ANSWER ---
    final_answer = init_answer
    try:
        is_correct = json.loads(review_answer).get("is_correct", True) 
        if not is_correct:
            final_prompt = MODIFIED_INIT_ANSWER_PROMPT.format(
                INIT_ANSWER=init_answer, 
                REVIEW=review_answer,
            )
            final_answer, latest_tokens = token_speed_calculator(
                "Refine Answer (1 Step)", token_log, latest_tokens, model,
                mes=final_prompt, system_prompt=""
            )
    except (json.JSONDecodeError, AttributeError):
        print("Warning: Review did not return valid JSON. Skipping refinement.")

    print("Final Answer:", final_answer, "\n")

    # --- CODE GENERATOR & FIX ---
    # 1) Generate initial code
    math_ans, latest_tokens = token_speed_calculator(
        "Code Generation", token_log, latest_tokens, model,
        mes=final_answer, system_prompt=CODE_GENERATOR_PROMPT.format(math_model_text=final_answer)
    )

    # 2) First pass through FIX_CODE_PROMPT to polish before execution
    F_FIX_CODE_PROMPT = FIX_CODE_PROMPT.format(
        code=math_ans,
        raw_problem=problem,
        raw_model=final_answer,
        classification_json=classification_json_str,
    )
    math_ans, latest_tokens = token_speed_calculator(
        "Code Fix Loop 1", token_log, latest_tokens, model,
        mes="Please ensure the code runs end-to-end and prints 'Objective value: <number>'.",
        system_prompt=F_FIX_CODE_PROMPT,
    )

    # Extract code from markdown fences
    math_code = _extract_code_from_markdown(math_ans)
    if math_code.strip() == "":
        math_code = math_ans
    print(f"Extracted Code:\n{math_code}\n")

    # Guard: forbid external I/O and enforce embedded raw context
    if _violates_io(math_code) or _missing_required_context(math_code):
        fix_mes = (
            "Detected forbidden external I/O or missing required embedded raw strings. "
            "Remove all external reads and ensure raw_problem_text/raw_model_text/raw_classification_json are present."
        )
        F_FIX_CODE_PROMPT = FIX_CODE_PROMPT.format(
            code=math_code,
            raw_problem=problem,
            raw_model=final_answer,
            classification_json=classification_json_str,
        )
        math_ans, latest_tokens = token_speed_calculator(
            "Code Fix Guard", token_log, latest_tokens, model,
            mes=fix_mes, system_prompt=F_FIX_CODE_PROMPT,
        )
        math_code = _extract_code_from_markdown(math_ans)
        if math_code.strip() == "":
            math_code = math_ans

    # 3) Execute once
    exec_output = run_generated_code(math_code)
    print(exec_output)

    # 4) Auto-debug loop if runtime failed or no objective printed
    max_auto_fixes = 3
    attempt = 0
    while (not _has_objective(exec_output) or _is_error_output(exec_output)) and attempt < max_auto_fixes:
        attempt += 1
        print(f"[Auto-Debug] Attempt {attempt}: objective missing or error detected. Re-invoking FIX_CODE_PROMPT…")
        # Build system prompt with original code, and pass error log as message
        F_FIX_CODE_PROMPT = FIX_CODE_PROMPT.format(
            code=math_code,
            raw_problem=problem,
            raw_model=final_answer,
            classification_json=classification_json_str,
        )
        fix_mes = (
            "Runtime error / logs from previous run:\n" + exec_output +
            "\n\nPlease fix the Python code so it runs successfully, embeds the three raw strings, performs no external I/O, "
            "and outputs a line of the exact form 'Objective value: <number>'. Return ONLY the corrected Python code in a fenced block."
        )
        math_ans, latest_tokens = token_speed_calculator(
            f"Auto Debug Fix {attempt}", token_log, latest_tokens, model,
            mes=fix_mes, system_prompt=F_FIX_CODE_PROMPT,
        )
        # Extract code and execute again
        math_code = _extract_code_from_markdown(math_ans)
        if math_code.strip() == "":
            math_code = math_ans
        print(f"[Auto-Debug] New code extracted (attempt {attempt}).")
        exec_output = run_generated_code(math_code)
        print(exec_output)

    # Final result text returned from solve()
    result = exec_output
    return result, token_log


def extract(pipeline_ans: str) -> float:
    # print("🌟 程式結果：", pipeline_ans)
    if not isinstance(pipeline_ans, str):
        return "不是字串"
    pattern = r"Objective value:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"  # [MOD] allow sci notation
    matches = re.findall(pattern, pipeline_ans)
    print(f"🌟 Matches found: {matches}")
    if not matches:
        return -99999.0
    return float(matches[-1])


def main():
    # argument 在此
    parser = argparse.ArgumentParser(
        prog="reasoning.py",
        description="LLM Reasoning for math problems"
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Path to a single .desc.txt file *or* a directory containing many .desc.txt files"
    )
    parser.add_argument(
        "-l", "--log", required=True,
        help="Path to output JSON file *or* a directory in which per‑problem logs will be created"
    )
    parser.add_argument(
        "-r", "--reasoning", required=False, default="high", choices=["medium", "high"],
        help="Reasoning effort sent to the OpenAI API ('medium' or 'high')"
    )
    args = parser.parse_args()

    global model
    model = OpenAIReasoning(api_key=api_key, reasoning_effort=args.reasoning)

    # ---- Support single file or directory input ----
    desc = args.input
    is_input_dir = os.path.isdir(desc)
    if is_input_dir:
        desc_files = sorted(
            [os.path.join(desc, f) for f in os.listdir(desc) if f.endswith(".desc.txt")],
            key=lambda p: int(re.search(r"q(\d+)", os.path.basename(p)).group(1))
        )
        if not desc_files:
            print(f"ERROR: no .desc.txt files found in directory {desc}")
            sys.exit(1)
    else:
        if not os.path.isfile(desc):
            print(f"ERROR: input file {desc} not found.")
            sys.exit(1)
        desc_files = [desc]

    # --- Helper to derive per‑problem thinking‑log path ---
    def _make_thinking_log_path(problem_id: int) -> str:
        if os.path.isdir(args.log):
            os.makedirs(args.log, exist_ok=True)
            return os.path.join(args.log, f"q{problem_id}_thinking.log" if problem_id else "thinking.log")
        else:
            base, ext = os.path.splitext(args.log)
            return f"{base}_thinking{ext or '.log'}"

    for desc_path in desc_files:
        problem_id_match = re.search(r"q(\d+)", os.path.basename(desc_path))
        problem_id = int(problem_id_match.group(1)) if problem_id_match else 0

        thinking_log_path = _make_thinking_log_path(problem_id)

        with open(desc_path, "r", encoding="utf-8") as f:
            problem_desc = f.read()

        ans_path = re.sub(r"\.desc\.txt$", ".ans.txt", desc_path)
        problem_ans = None
        if os.path.isfile(ans_path):
            with open(ans_path, "r") as f:
                problem_ans = f.readline().strip()

        # --- Capture all stdout during solve/extract ---
        log_buf = io.StringIO()
        with redirect_stdout(log_buf):
            pipeline_output, problem_token_log = solve(problem_desc)
            final_pipeline_ans = extract(pipeline_output)

        thinking_log_text = log_buf.getvalue()
        # Mirror captured output back to console
        print(thinking_log_text, end="")

        final_problem_ans = float(problem_ans) if problem_ans else None
        is_correct = False
        if final_problem_ans is not None:
            is_correct = abs(final_pipeline_ans - final_problem_ans) < 0.01

        log_data_to_save = {
            "problem_id": problem_id,
            "correctness": is_correct if problem_ans else None,
            "expected_answer": final_problem_ans,
            "pipeline_answer": final_pipeline_ans,
            "token_usage_by_step": problem_token_log
        }

        # Decide where to write the log
        if os.path.isdir(args.log):
            os.makedirs(args.log, exist_ok=True)
            log_path = os.path.join(
                args.log,
                f"q{problem_id}_log.json" if problem_id else "log.json"
            )
        else:
            # If args.log is given as a file path, always overwrite/append to that file.
            log_path = args.log

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data_to_save, f, indent=4, ensure_ascii=False)

        # Write thinking log
        with open(thinking_log_path, "w", encoding="utf-8") as f_think:
            f_think.write(thinking_log_text)


if __name__ == "__main__":
    main()
