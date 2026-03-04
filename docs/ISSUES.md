# Refactoring Issues

## Critical

### 1. Near-duplicate functions: gen_rnd_legacy() and gen_rnd()
- **Location:** `src/rnddag.py:103-261`
- **Issue:** These two functions are ~95% identical. The only differences are that `gen_rnd_legacy()` uses instance attributes while `gen_rnd()` accepts parameters with defaults, and `gen_rnd()` uses `.copy()` on list operations.
- **Recommendation:** Extract a shared `_generate_layer_by_layer()` helper that both methods call with normalized parameters.

### 2. Node/edge attribute assignment repeated 4 times
- **Locations:**
  - `src/daggen-cli.py:93-102` (single-DAG mode)
  - `src/daggen-cli.py:167-184` (multi-DAG mode)
  - `src/daggen-gui.py:289-294` (single-DAG mode)
  - `src/daggen-gui.py:343-348` (multi-DAG mode)
- **Issue:** The same pattern for generating execution times, setting node attributes, and computing edge weights is copy-pasted across four locations.
- **Recommendation:** Extract into a utility function, e.g. `apply_execution_times_to_dag(dag, n_nodes, workload, dummy=False)`.

## High

### 3. Empty DAGTaskset class
- **Location:** `src/rnddag.py:24-56`
- **Issue:** 6 methods defined but all are stubs with `pass`: `gen()`, `add()`, `remove()`, `dump()`, `load()`. Only initialization is tested.
- **Recommendation:** Either implement all methods or remove the class entirely.

### 4. daggen-gui.py is a god class
- **Location:** `src/daggen-gui.py` (485 lines, single class)
- **Issue:** Mixes UI creation/layout, parameter reading/validation, DAG generation logic, file I/O for config, and mode visibility management.
- **Recommendation:** Split into separate concerns: `DAGGenerationLogic`, `ConfigManager`, `ParameterValidator`.

### 5. Bare except clause
- **Location:** `src/daggen-cli.py:25`
- **Issue:** `except:` catches all exceptions without specificity. Swallows the original error context.
- **Recommendation:** Use specific exception types (`FileNotFoundError`, `json.JSONDecodeError`) and preserve context with `raise ... from e`.

## Medium

### 6. Commented-out dead code
- **Locations:**
  - `src/rnddag.py:158-159, 175, 177-178, 238-239, 255, 257-258, 311, 325, 333, 339, 369, 420`
  - `src/generator.py:26-28, 45`
- **Issue:** ~20 instances of commented-out code (conditional DAG logic, print statements, feasibility checks).
- **Recommendation:** Remove all commented code. Track incomplete features (e.g. conditional DAGs) as proper issues instead.

### 7. Inconsistent parameter passing across generation methods
- **Location:** `src/rnddag.py`
- **Issue:** `gen_rnd_legacy()` uses instance attributes (`self.parallelism`, etc.), `gen_rnd()` uses function parameters with defaults, `gen_nfj()` uses instance attributes again.
- **Recommendation:** Standardize on one approach across all generation methods.

### 8. Mixed logging and no logging configuration
- **Locations:**
  - `src/daggen-cli.py` uses `logging.info()` but never calls `logging.basicConfig()`
  - `src/generator.py` uses `print()` instead of logging
- **Recommendation:** Configure logging in `main()` and standardize on the `logging` module everywhere.

### 9. Unused import
- **Location:** `src/daggen-cli.py:14`
- **Issue:** Imports `time` but never uses it.
- **Recommendation:** Remove the import.

### 10. No-op list comprehension
- **Location:** `src/daggen-cli.py:130`
- **Issue:** `period_set = [(x) for x in period_set]` does nothing — parentheses don't create a copy or change the type.
- **Recommendation:** Remove or replace with `period_set = list(period_set)` if a copy is intended.

## Low

### 11. PEP 8 class naming violation
- **Location:** `src/daggen-gui.py:28`
- **Issue:** `class daggen_gui(QMainWindow)` uses snake_case instead of CamelCase.
- **Recommendation:** Rename to `DagGenGUI`.

### 12. Missing docstrings
- **Locations:** Most functions across all source files.
- **Issue:** No module-level docstrings; most functions lack parameter documentation.
- **Recommendation:** Add docstrings in a consistent style (Google or NumPy format).

### 13. DAG.L attribute never computed
- **Location:** `src/rnddag.py:67`
- **Issue:** `self.L = -1` is initialized with a comment "needs to be computed later" but is never computed anywhere.
- **Recommendation:** Implement critical path length computation or remove the attribute.

### 14. Infinite retry risk in utilization generation
- **Locations:**
  - `src/generator.py:31-43` (`uunifast_discard()`)
  - `src/generator.py:61-64` (`drs_gen()`)
- **Issue:** `while len(sets) < nsets:` loops with no iteration limit. If parameters are too restrictive, this loops forever.
- **Recommendation:** Add a max iteration limit with a clear error message.

### 15. Unsafe list mutation during iteration
- **Location:** `src/rnddag.py:155-157`
- **Issue:** `gen_rnd_legacy()` calls `nodes_orphan.remove(i)` while iterating over `nodes_orphan`. `gen_rnd()` correctly uses `.copy()` at line 235.
- **Recommendation:** Use `.copy()` in `gen_rnd_legacy()` as well, or consolidate with issue #1.

### 16. Conditional DAG UI elements disabled but not removed
- **Location:** `src/daggen-gui.py:141-143, 188-194`
- **Issue:** UI elements for conditional/MCS DAGs are present but disabled with "not yet implemented" tooltips.
- **Recommendation:** Either implement or remove entirely to reduce clutter.
