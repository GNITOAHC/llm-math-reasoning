CODE_GENERATOR_PROMPT = """
You are an expert software engineer specializing in Operations Research.
Convert the mathematical model below into a **stand-alone Python script**.

──────────────── Model ────────────────
{MATH_MODEL}
────────────────────────────────────────

**Requirements**

    1. You can use the `pulp` library or other library. Remember to import `PULP_CBC_CMD` to enable silent mode if you use pulp.
    2. Declare all decision variables with correct domains (Integer / Continuous).  
    3. **Build the objective and constraints EXACTLY as given in the mathematical model. Do NOT add, assume, or invent any new constraints that are not explicitly stated.**
      【新增指令】
        ### TSP Data Parsing and Cost Handling ###
        - If the problem is a TSP, your first task is to parse the problem data from the `{MATH_MODEL}`.
        - Locate the `[ADJACENCY_MATRIX]` section.
        - Extract the dimension `n` from the `Dimension:` metadata.
        - Create a Python dictionary called `costs` to store the distances.
        - Iterate from `i = 1` to `n` and `j = 1` to `n`. For each pair `(i, j)`, parse the floating-point distance from the matrix.
        - **IMPORTANT**: The official TSP cost is the **nearest integer** to the given distance. You MUST round each parsed distance to the nearest integer using `int(distance + 0.5)`. Store this integer cost in your `costs` dictionary, e.g., `costs[(i, j)] = int(raw_distance + 0.5)`.
        - The objective function in your Python script **MUST** be built using this integer `costs` dictionary.
        • For TSP/VRP:
            – If the mathematical model already specifies subtour‑elimination constraints, implement them exactly (e.g., MTZ or flow formulation).  
            – If the model *omits* such constraints, auto‑inject the standard MTZ set:  
              ‣ declare binary x[(i,j)] for all i ≠ j; do **not** create x[(i,i)] self‑loops or enforce x[(i,i)] == 0;  
              ‣ declare integer u[i] with bounds 1…n and add u[0] == 1;  
              ‣ add `u[i] - u[j] + n * x[(i,j)] <= n - 1` for all i ≠ 0, j ≠ 0, i ≠ j.  
            – Ensure every node has exactly one outgoing and one incoming arc (degree constraints).
    4. **Call the solver silently using `prob.solve(PULP_CBC_CMD(msg=False))`**. After solving, **print** the following, each on a new line:  
    - `Status: <Optimal/…>`  — use `LpStatus[prob.status]`  
    - One line per variable, e.g. `sled_dogs = 3`  
    - `Objective value: <value>`  
    5. Output **only** valid Python code — no Markdown, no comments outside `# …`".  
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
"""


FIX_CODE_PROMPT = """
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


{code}

Please provide the fixed code:
"""