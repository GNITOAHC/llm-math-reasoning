CODE_GENERATOR_PROMPT = '''
You are an expert software engineer specializing in Operations Research.
Convert the mathematical model below into a **stand-alone Python script**.

──────────────── Model ────────────────
{math_model_text}
────────────────────────────────────────

**Requirements**

1. You may use `pulp` (CBC) or other MILP libraries, and you MAY use **numpy**. Always import `PULP_CBC_CMD` to run silently. Use Python's `decimal.Decimal` with context precision ≥ 50 to recompute and print the final objective.

2. Declare all decision variables with correct domains (Integer / Binary / Continuous) exactly as in the model.

3. **Build the objective and constraints EXACTLY as given. Do NOT add or omit constraints.**

─────────────── TSP — Efficient Hybrid Strategy (MUST IMPLEMENT) ───────────────
If the model is a **TSP** and a `Dimension: n` can be parsed:

A) **Data precedence & parsing**
   - If `[ADJACENCY_MATRIX]` exists, parse it **as given** (authoritative).
   - **UPPER_ROW handling:** Accept either a full n-entry row or triangular rows (i lists entries for j>i). If triangular, reconstruct the full symmetric matrix by mirroring.
   - When header and data disagree, **trust the data layout** while still validating.

B) **TSPLIB weight policies & integerization**
   - `EXPLICIT`: use matrix values as costs. If all off-diagonals are integers, treat totals as exact integers. If decimals exist, detect minimal decimal step and quantize values and totals to that precision.
   - `EUC_2D / ATT`: if a full matrix is provided, use it as costs. Additionally build an **integerized matrix** by rounding each off-diagonal to nearest integer (TSPLIB style) and compute its tour total for audit; select the integerized total as the printed objective.
   - `GEO`:
       * If coordinates are available, compute TSPLIB GEO integer distances and use them.
       * If only a decimal matrix is present, and `max_offdiag ≤ 20` and `min_nonzero ≤ 0.25`, treat entries as **angular degrees**; scale 111.195 km/deg and round to integers. Otherwise treat entries as kilometers and round to nearest integer.
     Always also compute the raw Decimal matrix total for audit.

C) **Three-tier strategy (warm-start + exact where required)**
   1) **Heuristic warm-start**
      - Build many seeds (nearest-neighbour from multiple starts + random perms).
      - 2-opt to convergence, then limited 3-opt with 20-nearest candidate lists.
      - Keep the best `(tour_best, cost_best)` under the **active policy** (integerized when applicable).

   2) **Exact policy by size (MANDATORY)**
      - **n ≤ 60 → exact DFJ cutting-plane is MANDATORY.**
        * Build a MILP with binary x_{{i,j}}, degree=1 constraints.
        * Solve with CBC to integrality. Extract the support graph from the incumbent solution.
        * Detect subtours. For each subtour S with |S| ≥ 2, add a DFJ cut:  Σ_{{i∈S}} Σ_{{j∈S, j≠i}} x_{{i,j}} ≤ |S| − 1.
        * Re-solve and repeat until a single Hamiltonian tour is obtained. Use the heuristic tour as a warm start.
        * Do **not** terminate with a heuristic solution; keep iterating until **no subtours remain**. This is required.
      - 61–120 → Iterative DFJ cuts with warm-start. Time limit: n ≤ 80 → 900 s; 81–120 → 600 s.
      - n > 120 → Heuristic only; print `Status: Heuristic`.

   3) **Output selection**
      - If both heuristic and MILP produce tours, select the **lower-cost** tour under the current policy (integerized/scaled matrix when applicable). For `EXPLICIT` integer matrices, the final objective must match the exact MILP tour cost.

   4) **Verification**
      - Check each node appears exactly once; n edges in the tour.
      - Recompute tour cost with **Decimal** from the authoritative numeric matrix; assert equality within 5e-9 (and exact for integer matrices). If mismatch, print `OBJECTIVE_MISMATCH solver=<...> recomputed=<...>` and print the recomputed value as the final line.

   - Before solving the TSP, validate that the provided matrix is square (n×n). If not, immediately print: `ERROR: Input matrix must be square (n x n), but got shape (rows, cols).`

   - **For n ≤ 60, it is prohibited to return a heuristic-only answer.** The final line **must** be the exact integer objective from the DFJ MILP solution.

──────────── Universal data parsing & validation (ALL problems) ────────────
- Embed the string `{math_model_text}` as `raw_data = r"""{math_model_text}"""`.
- Parse `Dimension: n` when present. If absent, infer n from matrix row labels (max key) and print "Inferred Dimension: n".
- Validate: square n×n; zero diagonal; symmetry (list ≥10 mismatches then fail).
- Reject ellipses `…` or truncated rows → print `DATA_VALIDATION_FAILED` and raise.

- **Abort on validation errors:** print `DATA_VALIDATION_FAILED` and raise; do **not** print an objective.

──────────── Implementation rules ────────────
4. Solver calls:
   `prob.solve(PULP_CBC_CMD(msg=False, timeLimit=<seconds>))`
   Defaults: n ≤ 80 → 1800 s; 81–120 → 1500 s; otherwise 900 s.

5. After solving (or selecting heuristic):
   - Print `Status: <Optimal/Feasible/Heuristic/...>`
   - For MILP, print each used binary variable as `x_i_j = 1`.
   - Print audit lines:
       - `Raw matrix tour cost: <Decimal>`
       - If applicable: `Integerized tour cost: <int>`
       - If applicable: `GEO-scaled tour cost: <int>`
 - **Exactly one final line**: `Objective value: <number>` chosen per the policy above. For EXPLICIT matrices, match the expected optimal value exactly; any deviation is a failure.
'''


FIX_CODE_PROMPT = '''
You are a top-tier Python debugging expert.
User has provided a piece of may-problematic Python code.

Your task is to fix this code so that it executes correctly and return the fixed code.

- If the code solves a TSP with n ≤ 60, you **must implement an exact iterative DFJ cutting-plane MILP**. Heuristics are allowed only as warm starts. Do **not** return a heuristic objective for n ≤ 60. For n > 60 you may fall back to a heuristic if MILP times out.
- Respect the same data-validation, no external I/O, and output-contract rules.

Rules:
1. Fix any errors or issues.
2. Do not add explanations; return only the fixed code in a single fenced code block.
3. Maintain the embedded data strings exactly; no external files or toy data.

Common fixes:
- `TypeError: int() argument ... 'LpAffineExpression'` → use `pulp.value(...)` after solve.
- `AttributeError: 'list' object has no attribute 'values'` → iterate directly over `prob.variables()`.
- `KeyError` from `.format(...)` with `{}` inside strings → use f-strings or escape braces `{{ }}`.
- Floating-point drift → use `Decimal` with `getcontext().prec = 50` and recompute objective.

────────────────────────  CONTEXT ANCHORING  ────────────────────────
At the VERY TOP of the fixed script, define and validate the three embedded strings. They are the **only** data sources.

raw_problem_text = r"""{raw_problem}"""
raw_model_text = r"""{raw_model}"""
raw_classification_json = r"""{classification_json}"""

if not (isinstance(raw_problem_text, str) and raw_problem_text.strip() and
        isinstance(raw_model_text, str) and raw_model_text.strip() and
        isinstance(raw_classification_json, str) and raw_classification_json.strip()):
    print("DATA_VALIDATION_FAILED")
    raise RuntimeError("Missing required embedded context strings")

A. Rely exclusively on these strings (including `[ADJACENCY_MATRIX]` if present). If a required datum is missing, print `DATA_VALIDATION_FAILED` and raise with a precise reason.
B. **No external I/O**: remove `open(...)`, `argparse`, `sys.argv`.
C. **Output contract**: On success, print exactly one final line `Objective value: <number>`. On failure, print `DATA_VALIDATION_FAILED` and raise.
D. **TSP matrix & dimension enforcement**:
   - Parse the matrix verbatim. Robustly parse `k: [ ... ]` rows; ignore trailing commas/whitespace.
   - Parse `Dimension: <n>`; require rows 1..n each with exactly n entries.
   - If exactly one entry is missing and the symmetric counterpart exists, heal from symmetry; else fail.
   - Support `UPPER_ROW`: full rows or triangular rows; if triangular, expand and then validate.
   - Enforce zero diagonals and symmetry; list mismatches before raising.
   - Reject ellipses `…` or mentions of omitted rows.

E. **TSPLIB policies**:
   - `EXPLICIT`: use matrix as-is; integer totals if integers, else quantize to minimal decimal step.
   - `EUC_2D/ATT`: if matrix present, use it; also compute rounded-integer matrix totals and use that for the final objective.
   - `GEO`: with coordinates → TSPLIB GEO integers; without coordinates but decimal matrix → if max≤20 and min_nonzero≤0.25 treat as angular degrees ×111.195 km/deg then round; otherwise treat as kilometers and round. Always also compute the raw Decimal matrix total as an audit line.

Heuristic vs MILP:
- For n ≤ 60: return the MILP DFJ optimal tour only. The final `Objective value:` must equal the recomputed integer tour cost.
- For n > 60: if both produce feasible tours, select the lower recomputed **policy** cost and print only that in the final `Objective value:` line.

Finally, return ONLY the corrected Python code in a single fenced code block, like:

{code}
Please provide the fixed code:

'''