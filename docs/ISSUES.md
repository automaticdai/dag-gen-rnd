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

### ~~6. Commented-out dead code~~ SOLVED
- **Resolution:** Removed all commented-out code (debug prints, feasibility checks, commented plot calls) from `rnddag.py` and `generator.py`.

### ~~7. Inconsistent parameter passing across generation methods~~ SOLVED
- **Resolution:** All three generation methods now accept parameters with defaults: `gen_rnd()`, `gen_rnd_legacy()`, and `gen_nfj()`. Removed instance attribute configs from `DAG.__init__`.

### ~~8. Mixed logging and no logging configuration~~ SOLVED
- **Resolution:** Added `logging.basicConfig()` in `main()` and fixed `logging.info()` calls to use proper `%s` formatting. `generator.py` `__main__` block kept as `print()` since it's a manual test script.

### ~~9. Unused import~~ SOLVED
- **Resolution:** Removed unused `time` import from `src/daggen-cli.py`.

### ~~10. No-op list comprehension~~ SOLVED
- **Resolution:** Removed the no-op `[(x) for x in period_set]` line from `src/daggen-cli.py`.

## Low

### ~~11. PEP 8 class naming violation~~ SOLVED
- **Resolution:** Renamed `daggen_gui` to `DagGenGUI`.

### 12. Missing docstrings
- **Locations:** Most functions across all source files.
- **Issue:** No module-level docstrings; most functions lack parameter documentation.
- **Recommendation:** Add docstrings in a consistent style (Google or NumPy format).

### ~~13. DAG.L attribute never computed~~ SOLVED
- **Resolution:** Removed the unused `self.L` attribute from `DAG.__init__`.

### ~~14. Infinite retry risk in utilization generation~~ SOLVED
- **Resolution:** Added `MAX_ITERATIONS = nsets * 1000` limit to both `uunifast_discard()` and `drs_gen()`, raising `RuntimeError` with a descriptive message if exceeded.

### ~~15. Unsafe list mutation during iteration~~ SOLVED
- **Resolution:** Fixed as part of issue #1 — the shared `_generate_layer_by_layer()` uses `.copy()` correctly.

### ~~16. Conditional DAG UI elements disabled but not removed~~ SOLVED
- **Resolution:** Removed all conditional/MCS DAG UI widgets (`check_conditional`, `check_mcs_dag`, `edit_mcs`) and their associated layout rows and disabled-state code.
