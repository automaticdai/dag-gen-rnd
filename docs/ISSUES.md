# Refactoring Issues

## Critical

### ~~1. Near-duplicate functions: gen_rnd_legacy() and gen_rnd()~~ SOLVED
- **Location:** `src/rnddag.py:103-261`
- **Resolution:** Extracted shared `_generate_layer_by_layer()` helper; both methods are now thin wrappers. Also fixed #15 (unsafe list mutation) by using `.copy()` in the shared implementation.

### ~~2. Node/edge attribute assignment repeated 4 times~~ SOLVED
- **Resolution:** Extracted `apply_execution_times()` in `src/generator.py`; all 4 call sites now use it.

## High

### ~~3. Empty DAGTaskset class~~ SOLVED
- **Resolution:** Removed the dead `DAGTaskset` class from `src/rnddag.py` and all references in `daggen-cli.py`, `test_rnddag.py`, and `CLAUDE.md`.

### ~~4. daggen-gui.py is a god class~~ SOLVED
- **Resolution:** Extracted shared DAG generation logic into `src/dag_factory.py` with `generate_dag()` and `generate_multi_dag_taskset()`. Both CLI and GUI now call these factory functions instead of duplicating orchestration code.

### ~~5. Bare except clause~~ SOLVED
- **Resolution:** Changed bare `except:` to `except (FileNotFoundError, json.JSONDecodeError, OSError) as e:` with `raise ... from e` to preserve exception context.

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

### ~~8. Mixed logging and no logging configuration~~ SOLVED
- **Resolution:** Added `logging.basicConfig()` in `main()` and fixed `logging.info()` calls to use proper `%s` formatting. `generator.py` `__main__` block kept as `print()` since it's a manual test script.

### ~~9. Unused import~~ SOLVED
- **Resolution:** Removed unused `time` import from `src/daggen-cli.py`.

### ~~10. No-op list comprehension~~ SOLVED
- **Resolution:** Removed the no-op `[(x) for x in period_set]` line from `src/daggen-cli.py`.

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

### ~~15. Unsafe list mutation during iteration~~ SOLVED
- **Resolution:** Fixed as part of issue #1 — the shared `_generate_layer_by_layer()` uses `.copy()` correctly.

### 16. Conditional DAG UI elements disabled but not removed
- **Location:** `src/daggen-gui.py:141-143, 188-194`
- **Issue:** UI elements for conditional/MCS DAGs are present but disabled with "not yet implemented" tooltips.
- **Recommendation:** Either implement or remove entirely to reduce clutter.
