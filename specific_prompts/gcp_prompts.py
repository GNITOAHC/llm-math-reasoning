CODE_GENERATOR_PROMPT = '''
You are an expert software engineer specializing in Operations Research.
Convert the mathematical model below into a **stand-alone Python script**.

──────────────── Model ────────────────
{math_model_text}
────────────────────────────────────────

**Requirements**

    1. You can use the `pulp` library or other library. Remember to import `PULP_CBC_CMD` to enable silent mode if you use pulp.
    2. Declare all decision variables with correct domains (Integer / Continuous).
    3. **Build the objective and constraints EXACTLY as given …**
       ### DATA-PARSING RULES ###

       ── A. Graph-Coloring (EdgeList) ──
       * If `raw_model_text` contains a block that begins with `EdgeList:`,
         parse the subsequent lines `(u,v)`.
       * Determine vertex set V:
           - If a line `Dimension: n` (or `|V|: n`) exists, use it.
           - Else set `n = max(max(u,v) for (u,v) in E)` and V = {{1,…,n}}.
       * Number of colors K:
           - If the model text provides an explicit K, use it.
           - Otherwise set `K = n` (upper bound).
       * Validation:
           1) 1 ≤ u < v ≤ n; no self-loops, no duplicates.
           2) If a trailing comment `# |E| = m` is present, assert |E| = m.
       * Failure path: print `DATA_VALIDATION_FAILED`, show diagnostics, then
         `raise RuntimeError("EDGE_LIST_VALIDATION_FAILED")`.
       * Build ILP:
           - Binary x[(v,k)] and y[k] (if y appears in the model).
           - Degree/adjacency constraints exactly as in the model.
           - Objective as in the model; if model minimizes colors and no y[k] were
             provided, inject the standard linking `x[v,k] ≤ y[k]` and objective
             `min Σ y[k]`, because that is part of the provided mathematical model.

      ── B. TSP Data Parsing and Cost Handling ──
      (keep your existing full TSP block unchanged)

      4. Solve silently …
      5. Output only valid Python code …
      6. After printing the solution, add a verification step:
         • For GCP:
            - Check each vertex has exactly one color: Σ_k x[v,k] = 1.
            - For every edge (u,v) and color k: x[u,k] + x[v,k] ≤ 1.
            - Link: x[v,k] ≤ y[k] (when y is present).
            - Print the maximum left-hand-side violation found (should be 0).
         • For TSP keep your existing verification rules.

      
      B. ### TSP Data Parsing and Cost Handling ###
      - **Input formats to parse:** The `{math_model_text}` may 包含字典風格矩陣列，如 `k: [v1, v2, …]`。程式必須以正規表示式強韌解析此格式，去除空白與結尾逗號，依列索引 `k` 建立每列清單。
      - **Self-contained parsing — no external files or argv:** The script must embed `raw_data = r"""{math_model_text}"""` and parse **from this string only**. Do **not** read from files, `sys.argv`, or `argparse`. If command-line flags (e.g., `--start`) appear in `sys.argv`, **ignore them**. The program must succeed solely from `raw_data` and must not open any file.
      - **Authoritative precedence for building costs:**
        1) If the problem text contains a block labelled `[ADJACENCY_MATRIX]`, you MUST parse this matrix **verbatim** and use it as the cost matrix — **regardless of** the declared `Edge weight type`. Do not recompute from coordinates when a full matrix is supplied. Do not rescale, round, or otherwise alter the entries. Integers and decimals are both acceptable. If decimals are given, store them as Python `float` values.
        2) Else, if no matrix is provided but an `Edge weight type` is declared with coordinates, compute pairwise costs according to that rule:
           • **EUC_2D / EUC_3D:** Euclidean distance, rounded to nearest integer (`int(math.sqrt(...) + 0.5)`).
           • **CEIL_2D:** Euclidean distance rounded **up** (`math.ceil`).
           • **MAN_2D / MAN_3D:** Manhattan distance, rounded to nearest integer.
           • **MAX_2D / MAX_3D:** Chebyshev (maximum) norm, rounded to nearest integer.
           • **GEO:** Use the TSPLIB spherical formula with earth radius 6378.388 and `int(distance)` as in TSPLIB.
           • **ATT (pseudo‑Euclidean):** For points `i=(x_i,y_i)`, `j=(x_j,y_j)`, compute  
             `value = sqrt(((x_i-x_j)^2 + (y_i-y_j)^2)/10.0)`; then apply TSPLIB rounding: let `d = nint(value)` (nearest integer, halves rounded up); if `d < value`, set `d = d + 1`. Use `d` as the integer cost.  
           These rules mirror TSPLIB95.
      - **Declared Dimension enforcement (must implement):** The code **must parse** a line of the form `Dimension: <n>` (case-insensitive for `Dimension`). Let this be `declared_n`. After parsing rows, assert that indices `1..declared_n` are **all present** and that **exactly** `declared_n` rows are found. Also assert that every row has **exactly** `declared_n` numeric entries. **Do not** silently truncate or pad rows. If any check fails, print `DATA_VALIDATION_FAILED` and a diagnostics section listing: the `declared_n`, the set of present row indices, any missing indices, and for each row its detected length. Then raise `RuntimeError("Declared dimension mismatch or incomplete adjacency matrix")`.
      - **Matrix validation (must implement):** After parsing/building `costs`, assert:
         1) `n == declared_n` and the matrix is `n x n` with no `None` values;
         2) diagonal entries are zero (if a nonzero diagonal is found, list the offending indices in diagnostics); **remember that rows are 1-indexed while Python lists are 0-indexed — use `rows[i-1][i-1]` when checking diagonal**;
         3) symmetry holds `costs[(i,j)] == costs[(j,i)]` for **all** `i != j`; if violations exist, list a sample of at least 10 mismatches and then fail;
         4) print two sample entries (e.g., `(1,2)` and `(2,1)`).
         If any check fails, print `DATA_VALIDATION_FAILED` and the diagnostics before raising `RuntimeError("Invalid or missing adjacency matrix")`.
      - **Ellipsis/placeholder rejection (must implement):** If the parsed `raw_data` contains any ellipsis character `…` or patterns like `rows 4–75 omitted`, **treat this as a hard error**: print `DATA_VALIDATION_FAILED` with a message `ELLIPSIS_FOUND` and raise. **Never** substitute a toy/smaller matrix (e.g., `Dimension: 4`).
      - **Robust parsing & auto-heal:** If validation fails due to row-length mismatches, attempt a conservative repair **without inventing numbers**:
         1) Determine `declared_n` from the `Dimension:` line. **Never** derive `n` from contiguous row indices.
         2) If a row `i` is missing **exactly one** entry and the matrix is intended to be symmetric, try to fill the missing value `(i,j)` from the known symmetric counterpart `(j,i)`. If more than one entry is missing in any row, fail.
         3) If multiple rows are missing values but each missing location `(i,j)` has a symmetric counterpart `(j,i)`, fill all such cells from symmetry.
         4) After auto-heal, re-run the full validation. If any gap remains or symmetry value is unavailable, print a detailed diagnostics report listing each problematic row and column and then raise `RuntimeError("Adjacency matrix is not square or not symmetric after auto-heal")`. Do **not** proceed to solve if validation fails.
         5) Never guess costs from coordinates when a matrix is present, and never pad with zeros except along the diagonal.
      - **Subtour elimination for TSP/VRP:** – If the mathematical model already specifies subtour‑elimination constraints, implement them exactly.  
         – If the model omits them, auto‑inject standard MTZ: declare binary `x[(i,j)]` for all `i ≠ j`, integer `u[i]` with bounds `1…n`, fix `u[1] = 1`, and add `u[i] - u[j] + n * x[(i,j)] <= n - 1` for all `i ≠ 1, j ≠ 1, i ≠ j`.  
         – Enforce exactly one outgoing and one incoming arc per node (degree constraints).
         - **Graceful failure message:** If data validation ultimately fails, print a clear message `DATA_VALIDATION_FAILED` and the diagnostics before raising the exception. Do not print placeholder objective values like `-99999`.
      - **Implementation reminder:** Define `raw_data = r"""{math_model_text}"""` at the top of the script and pass it to the parser function (e.g., `n, costs = parse_from_raw(raw_data)`). **Do not alter or shorten `raw_data`.**
      
    4. **Call the solver silently using `prob.solve(PULP_CBC_CMD(msg=False))`**. After solving, **print** the following, each on a new line:  
    - `Status: <Optimal/…>`  — use `LpStatus[prob.status]`  
    - One line per variable, e.g. `sled_dogs = 3`  
    - `Objective value: <value>`  
    5. Output **only** valid Python code — no Markdown, no comments outside `# …`.
    6. **After printing the solution, add a verification step. For each constraint, print the calculated left-hand side value and show that it satisfies the constraint. This confirms the solver's answer is truly feasible.**
    7. **Verification Rule:** When calculating constraint values for verification (after `prob.solve()`), you MUST wrap each variable with `pulp.value()`.
    - **Correct:** `print(3 * pulp.value(x) + 2 * pulp.value(y))`
    - **Incorrect:** `print(3*x + 2*y)`

IMPORTANT: When using the 'pulp' library, you MUST follow these specific rules:

1.  **Constraint Definition:** Constraints MUST be added to the problem object using the `+=` operator. Do NOT use standard Python comparison operators like `<` or `>` by themselves.
    * **Correct:** `model += x + y <= 10, "Description"`
    * **Incorrect:** `x + y < 10`
    * **Incorrect:** `model += x + y < 10`

2.  **Comparison Operators:** For constraints, only use `<=`, `>=`, or `==`. The standard `<` and `>` operators are not supported for defining constraints and will cause a TypeError.

3.  **Variable and Constraint Names:** All variable and constraint names MUST be strings without spaces. Use underscores `_` instead of spaces. The warning `Spaces are not permitted in the name` indicates you are violating this rule.
    * **Correct:** `LpVariable("shipping_cost")`
    * **Incorrect:** `LpVariable("shipping cost")`

'''


FIX_CODE_PROMPT = '''
You are a top-tier Python debugging expert.
User has provided a piece of may-problematic Python code.

Your task is to fix this code so that it executes correctly and return the fixed code.

Rules:
1. Fix any errors or issues in the code.
2. Do not add any comments or explanations.
3. **IMPORTANT**: Return the same format as provided, without any additional text or formatting.
4. TypeError: '<' not supported between instances of 'LpVariable' and 'LpVariable'
The may-problematic code is as follows:
5. A very common error is:
`TypeError: int() argument must be a string, a bytes-like object or a real number, not 'LpAffineExpression'`

This error occurs when trying to treat a PuLP expression (like `3*x + 2*y`) as a simple number before its value has been extracted.

**To fix this, you MUST use the `pulp.value()` function to get the numerical result from variables or expressions AFTER the model has been solved (i.e., after `prob.solve()`).**
- **Incorrect:** `int(3*x + 2*y)`
- **Correct:** `int(pulp.value(3*x + 2*y))` or `int(3 * pulp.value(x) + 2 * pulp.value(y))`

6. Another frequent error is:
`AttributeError: 'list' object has no attribute 'values'`

This typically occurs when trying to iterate over the variables of a PuLP problem. The `prob.variables()` method returns a **list** of `LpVariable` objects, not a dictionary. Lists do not have a `.values()` method.

**To fix this, you must iterate directly over the list returned by `prob.variables()`.**
- **Incorrect:** `for v in prob.variables().values():`
- **Incorrect:** `for v in prob._variables.values():`
- **Correct:** `for v in prob.variables():`

────────────────────────  CONTEXT ANCHORING (ANTI‑TOY‑DATA)  ────────────────────────
At the VERY TOP of the fixed script, define and validate the following three embedded strings. They must be used as the **only** sources of problem data. Do **not** read files, `sys.argv`, or fabricate toy data.

raw_problem_text = r"""{raw_problem}"""
raw_model_text = r"""{raw_model}"""
raw_classification_json = r"""{classification_json}"""

if not (isinstance(raw_problem_text, str) and raw_problem_text.strip() and
        isinstance(raw_model_text, str) and raw_model_text.strip() and
        isinstance(raw_classification_json, str) and raw_classification_json.strip()):
    print("DATA_VALIDATION_FAILED")
    raise RuntimeError("Missing required embedded context strings")

A. The program MUST rely exclusively on these three variables (plus any data blocks already present **inside** them, e.g., `[ADJACENCY_MATRIX]`). It is **forbidden** to introduce `items = [...]`, toy matrices, synthetic capacities, or default CSVs. If a required datum cannot be found inside these strings, print `DATA_VALIDATION_FAILED` and raise with a precise explanation.

B. **No external I/O**: Remove any use of `open(...)`, `argparse`, or `sys.argv` for data. Parsing must come from `raw_problem_text` / `raw_model_text`.

C. **Output contract**: On success, print exactly **one** line of the form `Objective value: <number>` after the variable listings. On failure (validation errors), **do not** print an objective; print `DATA_VALIDATION_FAILED` and raise.

D. **EdgeList enforcement (for Graph-Coloring):**
   * If `EdgeList:` appears in `raw_model_text`, the fixed script must:
     - Parse all edges `(u,v)` from the embedded text only.
     - Derive `n` and `K` as specified: if K missing, set `K = n`.
     - Create binary `x[(v,k)]` and `y[k]` (when model minimizes colors).
     - Add constraints: assignment, adjacency, linking.
     - Prohibit any external files. If detected, print `DATA_VALIDATION_FAILED`
       and raise.
   * After solving, print one line `Objective value: <number>` and also print
     each vertex’s color (e.g., `color[1] = 3`) before the objective line.

E. **TSP adjacency matrix & dimension enforcement** (if applicable):
7. For TSP problems where an `[ADJACENCY_MATRIX]` is supplied, parse that matrix verbatim and build `costs` directly from it. Remove any fabricated coordinates or instance names (e.g., `BAYS29`) unless explicitly present in the input.
8. Implement a robust dictionary-style matrix parser: accept lines like `k: [ ... ]`, ignore trailing commas/whitespace, and build the `matrix` in row-index order. If some rows have one missing entry but the symmetric counterpart exists, fill it from symmetry; otherwise raise a `RuntimeError` with a diagnostics list. Print `DATA_VALIDATION_FAILED` before raising. Never fabricate costs.
9. **Dimension enforcement:** Parse `Dimension: <n>`. If rows 1..n are not all present, or any row does not contain exactly `n` entries, print `DATA_VALIDATION_FAILED` with diagnostics and raise `RuntimeError`. Do not infer `n` from contiguous rows and do not truncate rows.
10. **No silent padding/truncation:** If a row has more or fewer than `n` values, treat it as an error (except the single-cell symmetry auto-heal described above). Never drop extra values or pad with zeros.
11. **Full symmetry check:** Verify `matrix[i][j] == matrix[j][i]` for all `i != j`; list mismatches if any, then raise.
12. **Abort on validation errors:** If validation fails, do not print an objective; ensure the program exits after raising, so upstream detects the failure and triggers a fix cycle.
13. **Indexing pitfall (diagonal/symmetry):** Rows are labeled 1..n in the text, but Python lists are 0-indexed. When checking diagonals and symmetry on `rows`, use `rows[i-1][i-1]` for diagonals and compare `rows[i-1][j-1]` with `rows[j-1][i-1]`.
14. **Ellipsis rejection / no toy matrices:** If the input contains `…` or mentions omitted rows (e.g., `rows 4–75 omitted`), print `DATA_VALIDATION_FAILED` and raise. Do **not** substitute a small `Dimension: 4` dataset. Always parse the full matrix from `raw_problem_text` / `raw_model_text`.

F. **PuLP safety rules** (must follow):
- Add constraints only via `prob += ...` using `<=`, `>=`, or `==`. Never write bare comparisons like `x + y < 10`.
- Name variables/constraints with strings without spaces.
- When printing verification, always wrap variables in `pulp.value(...)`.

Finally, return ONLY the corrected Python code in a single fenced code block, like:
```python
# <fixed script here>
```

{code}
Please provide the fixed code:
'''