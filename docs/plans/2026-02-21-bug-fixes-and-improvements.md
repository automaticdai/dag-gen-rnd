# Bug Fixes and Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all identified bugs, code quality issues, and test gaps across the dag-gen-rnd codebase.

**Architecture:** Fixes are grouped by file/concern. Each task is independent except where noted. All changes follow TDD: write the failing test first, then implement the fix.

**Tech Stack:** Python 3.7+, pytest, networkx, pygraphviz (optional), numpy

---

## Task 1: Fix `pygraphviz` unconditional top-level import

**Files:**
- Modify: `src/rnddag.py:14-15`

**Problem:** `import pygraphviz as pgv` at line 15 crashes the entire module if pygraphviz is not installed. The `pgv` alias is never used. `graphviz_layout` and `to_agraph` (imported line 14) are only needed in `save()` and `__str__`.

**Step 1: Write the failing test**

In `tests/test_rnddag.py`, add to `TestDAGInit`:

```python
def test_module_importable_without_pygraphviz(self):
    """Importing rnddag should not require pygraphviz at module level."""
    import importlib, sys
    # Simulate missing pygraphviz by temporarily removing it
    pgv_mod = sys.modules.pop('pygraphviz', None)
    try:
        if 'rnddag' in sys.modules:
            del sys.modules['rnddag']
        import rnddag  # Should not raise ImportError
        d = rnddag.DAG()
        d.gen_rnd()
        assert d.get_number_of_nodes() > 0
    finally:
        if pgv_mod is not None:
            sys.modules['pygraphviz'] = pgv_mod
```

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestDAGInit::test_module_importable_without_pygraphviz -v
```
Expected: FAIL (ImportError on pygraphviz) or ERROR

**Step 3: Implement the fix**

In `src/rnddag.py`, replace lines 14-15:
```python
# REMOVE these two lines:
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv
```

Then update `__str__` (around line 83):
```python
def __str__(self):
    from networkx.drawing.nx_agraph import to_agraph
    A = to_agraph(self.G)
    return A.__str__()
```

And update `save()` — replace the `A = nx.nx_agraph.to_agraph(...)` block (around line 382-384):
```python
if save_png:
    from networkx.drawing.nx_agraph import to_agraph
    A = to_agraph(self.G)
    A.layout(prog='dot')
    A.draw(os.path.join(basefolder, self.name + '.png'), format="png")
```

**Step 4: Run test to verify it passes**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestDAGInit::test_module_importable_without_pygraphviz -v
```
Expected: PASS

**Step 5: Run full test suite to check no regressions**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py -v
```

**Step 6: Commit**

```bash
git add src/rnddag.py tests/test_rnddag.py
git commit -m "fix: make pygraphviz a lazy import in rnddag.py"
```

---

## Task 2: Fix `gen_rnd_legacy()` orphan iteration bug

**Files:**
- Modify: `src/rnddag.py`
- Test: `tests/test_rnddag.py`

**Problem:** `gen_rnd_legacy()` at line ~155 iterates `nodes_orphan` while calling `.remove()` on it, silently skipping every other orphan. `gen_rnd()` already fixed this with `.copy()`.

**Step 1: Write the failing test**

Add a new test class to `tests/test_rnddag.py`:

```python
class TestGenRndLegacy:
    def setup_method(self):
        random.seed(42)
        self.dag = DAG()
        self.dag.gen_rnd_legacy()
        self.G = self.dag.get_graph()

    def test_produces_dag(self):
        assert isinstance(self.G, nx.DiGraph)
        assert nx.is_directed_acyclic_graph(self.G)

    def test_has_single_source(self):
        sources = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]
        assert len(sources) == 1

    def test_has_single_sink(self):
        sinks = [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
        assert len(sinks) == 1

    def test_is_weakly_connected(self):
        assert nx.is_weakly_connected(self.G)

    def test_dispatch_legacy_structural(self):
        """gen('legacy') should produce a valid DAG via dispatch."""
        random.seed(42)
        d = DAG()
        d.gen("legacy")
        G = d.get_graph()
        assert nx.is_weakly_connected(G)
        sources = [n for n in G.nodes() if G.in_degree(n) == 0]
        assert len(sources) == 1
```

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestGenRndLegacy -v
```
Expected: One or more tests FAIL (weakly_connected or single_source fails due to orphans not being connected)

**Step 3: Implement the fix**

In `src/rnddag.py`, locate the two orphan-removal loops in `gen_rnd_legacy()`. Change both from direct iteration to copy-based:

First occurrence (inside the per-layer loop, ~line 154):
```python
# BEFORE:
for i in nodes_orphan:
    nodes_orphan.remove(i)
    G.add_edge(1, i)

# AFTER:
for i in nodes_orphan.copy():
    G.add_edge(1, i)
    nodes_orphan.remove(i)
```

Second occurrence (after the loop, ~line 170):
```python
# BEFORE:
for i in nodes_orphan:
    nodes_orphan.remove(i)
    G.add_edge(1, i)

# AFTER:
for i in nodes_orphan.copy():
    G.add_edge(1, i)
    nodes_orphan.remove(i)
```

**Step 4: Run test to verify it passes**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestGenRndLegacy -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/rnddag.py tests/test_rnddag.py
git commit -m "fix: use .copy() in gen_rnd_legacy() orphan removal loops"
```

---

## Task 3: Fix `gen_nfj()` missing single-sink test

**Files:**
- Test: `tests/test_rnddag.py`

**Problem:** `TestGenNfj` has no test checking for a single sink node.

**Step 1: Add the missing test**

In `tests/test_rnddag.py`, add to `TestGenNfj`:

```python
def test_has_single_sink(self):
    sinks = [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
    assert len(sinks) == 1
```

**Step 2: Run test**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestGenNfj::test_has_single_sink -v
```
Expected: PASS (or reveals a real gen_nfj bug)

**Step 3: Commit**

```bash
git add tests/test_rnddag.py
git commit -m "test: add single-sink assertion for gen_nfj"
```

---

## Task 4: Fix `logging.info()` incorrect multi-arg calls in CLI

**Files:**
- Modify: `src/daggen-cli.py:58,199`

**Problem:** `logging.info("Configurations:", config)` passes `config` as a positional arg for `%s` substitution, but there's no `%s` in the format string, so `config` is silently dropped. Same issue on line 199.

**Step 1: Write the failing test**

In `tests/test_cli.py`, add to `TestParseConfiguration`:

```python
def test_logging_does_not_raise(self, tmp_path, sample_config):
    """Logging calls in main() should not raise TypeError."""
    import logging
    sample_config["global"]["save_to_file"] = False
    sample_config["global"]["print_DAG"] = True
    sample_config["global"]["multi-DAG_on"] = True
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(sample_config))
    # Should complete without TypeError from bad logging.info calls
    main(config_path=str(config_path), data_path=str(tmp_path / "data"))
```

Note: `logging.info()` with extra args doesn't raise by default, it just silently drops them. Add a basicConfig to surface errors:

```python
def test_logging_format(self, tmp_path, sample_config):
    """logging.info with multi-args must use %s format."""
    import logging, io
    handler = logging.StreamHandler(io.StringIO())
    handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    try:
        sample_config["global"]["save_to_file"] = False
        sample_config["global"]["multi-DAG_on"] = True
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))
        output = handler.stream.getvalue()
        assert "Total U:" in output
    finally:
        root_logger.removeHandler(handler)
```

**Step 2: Run test**

```bash
conda run -n dag-gen-rnd pytest tests/test_cli.py::TestParseConfiguration::test_logging_format -v
```
Expected: FAIL — "Total U:" not found in output (args are dropped)

**Step 3: Implement the fix**

In `src/daggen-cli.py`, fix the two bad logging calls:

Line ~58:
```python
# BEFORE:
logging.info("Configurations:", config)
# AFTER:
logging.info("Configurations: %s", config)
```

Line ~199:
```python
# BEFORE:
logging.info("Total U:", sum(U_p), U_p)
# AFTER:
logging.info("Total U: %s %s", sum(U_p), U_p)
```

Also add `logging.basicConfig()` at the top of `main()` so log messages are visible when the script is run:

```python
def main(config_path=None, data_path=None):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ...
```

**Step 4: Run test**

```bash
conda run -n dag-gen-rnd pytest tests/test_cli.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/daggen-cli.py tests/test_cli.py
git commit -m "fix: correct logging.info format args and add basicConfig"
```

---

## Task 5: Fix `gen_execution_times` ZeroDivisionError with `n=2, dummy=True`

**Files:**
- Modify: `src/generator.py:108-115`
- Test: `tests/test_generator.py`

**Problem:** When `dummy=True` and `n=2`, the inner loop runs 0 times (`n-2=0`), `w_p=0`, then `f = w_p / w` → `0 / w` ... wait, actually `f = w_p / w` would be `0 / (w-2)`. Then for `i in range(0)` loop doesn't run. But `c_dict[n] = 1` tries to set `c_dict[2]=1`. Actually the issue is: `w = w - 2` sets w to possibly negative, and `w_p = 0`, so `f = 0 / (w - 2)`. If original w was small (like w=2), w becomes 0 → `ZeroDivisionError`. Even with n=2 and any w, there are 0 internal nodes and the dict only has keys 1 and 2, which is correct, but `f = 0 / w` (if w-2 = 0) fails.

Actually the real issue: with `n=2, dummy=True`, n-2=0, the for loop doesn't run, `c_set=[]`, `w_p = sum([]) = 0`. Then `f = w_p / w` where `w = original_w - 2`. If original w is, say, 10, then `w=8`, `f = 0/8 = 0`. Then the for loop `range(n-2) = range(0)` doesn't execute. The dict gets `c_dict[1]=1` and `c_dict[2]=1`. This actually works! But if original w=2, then w=0 after subtraction → `f = 0/0` → ZeroDivisionError.

More practically, if n=3, dummy=True: n-2=1, loop runs once, c_set=[c], w=original_w-2, w_p=c, f=c/(original_w-2). If original_w=2, w=0 → ZeroDivisionError again.

The safe fix: guard against w <= 0 after subtraction, or guard n < 3 when dummy=True.

**Step 1: Write the failing test**

In `tests/test_generator.py`, add to `TestGenExecutionTimes`:

```python
def test_dummy_minimum_nodes(self):
    """n=2 with dummy=True: only source and sink, no crash."""
    c = gen_execution_times(n=2, w=10, round_c=True, dummy=True)
    assert c[1] == 1  # source
    assert c[2] == 1  # sink
    assert len(c) == 2

def test_dummy_small_w_no_crash(self):
    """Small w with dummy=True should not ZeroDivisionError."""
    c = gen_execution_times(n=4, w=2, round_c=False, dummy=True)
    assert c[1] == 1
    assert c[4] == 1
```

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_generator.py::TestGenExecutionTimes::test_dummy_minimum_nodes tests/test_generator.py::TestGenExecutionTimes::test_dummy_small_w_no_crash -v
```
Expected: FAIL or ERROR (ZeroDivisionError or wrong output)

**Step 3: Implement the fix**

In `src/generator.py`, update the `dummy=True` branch:

```python
else:
    # a dummy source / sink node only has unit execution times
    # -> exclude them from the generation process
    # -> append them at the last

    # dummy source node
    c_dict[1] = 1

    internal_n = n - 2
    if internal_n > 0:
        for i in range(internal_n):
            c = random.random()
            c_set.append(c)

        # normalise to w & assign to the execution time list
        w_internal = w - 2  # remove c(source) and c(sink)
        c_dict_internal = {}
        w_p = sum(c_set)
        if w_p > 0 and w_internal > 0:
            f = w_p / w_internal
            for i in range(internal_n):
                if round_c is False:
                    c_dict[i + 2] = c_set[i] / f
                else:
                    c_dict[i + 2] = max(round(c_set[i] / f), 1)
        else:
            # degenerate case: give all internal nodes c=1
            for i in range(internal_n):
                c_dict[i + 2] = 1

    # dummy sink node
    c_dict[n] = 1
```

Note: the original code used `if round_c == False` — keep using `is False` or `not round_c` for consistency. Match surrounding style.

**Step 4: Run tests**

```bash
conda run -n dag-gen-rnd pytest tests/test_generator.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/generator.py tests/test_generator.py
git commit -m "fix: guard ZeroDivisionError in gen_execution_times with dummy=True"
```

---

## Task 6: Add max-iteration guard to utilization generators

**Files:**
- Modify: `src/generator.py`
- Test: `tests/test_generator.py`

**Problem:** `uunifast_discard()` and `drs_gen()` loop indefinitely when constraints are unsatisfiable (e.g., `u > n * ulimit`). They should raise a clear error after a timeout.

**Step 1: Write the failing test**

In `tests/test_generator.py`, add:

```python
class TestUunifastGuard:
    def test_raises_on_impossible_constraints(self):
        """Should raise RuntimeError if ulimit makes the problem unsatisfiable."""
        with pytest.raises(RuntimeError, match="could not generate"):
            uunifast_discard(n=3, u=3.0, nsets=1, ulimit=0.1)
```

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_generator.py::TestUunifastGuard -v
```
Expected: FAIL (hangs or returns wrong error)

**Step 3: Implement the fix**

In `src/generator.py`, update `uunifast_discard()`:

```python
def uunifast_discard(n, u, nsets, ulimit=1, max_iterations=10000):
    sets = []
    iterations = 0
    while len(sets) < nsets:
        iterations += 1
        if iterations > max_iterations:
            raise RuntimeError(
                "uunifast_discard could not generate %d sets after %d iterations. "
                "Check that u <= n * ulimit." % (nsets, max_iterations)
            )
        utilizations = []
        sumU = u
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)
        if all(ut <= ulimit for ut in utilizations):
            sets.append(utilizations)
    return sets
```

Do the same for `drs_gen()`:

```python
def drs_gen(n, u, nsets, ulimit=1, max_iterations=10000):
    from drs import drs
    sets = []
    iterations = 0
    while len(sets) < nsets:
        iterations += 1
        if iterations > max_iterations:
            raise RuntimeError(
                "drs_gen could not generate %d sets after %d iterations." % (nsets, max_iterations)
            )
        vec = drs(n=n, sumu=u, upper_bounds=[ulimit] * n)
        if all(v >= 0 for v in vec):
            sets.append(list(vec))
    return sets
```

**Step 4: Run tests**

```bash
conda run -n dag-gen-rnd pytest tests/test_generator.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/generator.py tests/test_generator.py
git commit -m "fix: add max_iterations guard to uunifast_discard and drs_gen"
```

---

## Task 7: Make DAG generation algorithm configurable

**Files:**
- Modify: `config.json`
- Modify: `src/daggen-cli.py`
- Modify: `tests/conftest.py`
- Test: `tests/test_cli.py`

**Problem:** `gen_rnd()` is hardcoded in the CLI. Config has no `algorithm` key. Users cannot switch to `nfj` or `legacy` via config.

**Step 1: Write the failing test**

In `tests/test_cli.py`, add:

```python
class TestAlgorithmSelection:
    def test_nfj_algorithm_single_dag(self, tmp_path, sample_config):
        """CLI should use nfj algorithm when configured."""
        sample_config["global"]["multi-DAG_on"] = False
        sample_config["global"]["save_to_file"] = False
        sample_config["dag_config"]["algorithm"] = "nfj"
        sample_config["single-DAG"]["set_number"] = 2
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))

    def test_legacy_algorithm_single_dag(self, tmp_path, sample_config):
        """CLI should use legacy algorithm when configured."""
        sample_config["global"]["multi-DAG_on"] = False
        sample_config["global"]["save_to_file"] = False
        sample_config["dag_config"]["algorithm"] = "legacy"
        sample_config["single-DAG"]["set_number"] = 2
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))

    def test_default_algorithm_is_rnd(self, tmp_path, sample_config):
        """When algorithm key is absent, default is 'rnd'."""
        sample_config["global"]["multi-DAG_on"] = False
        sample_config["global"]["save_to_file"] = False
        # No 'algorithm' key in dag_config
        assert "algorithm" not in sample_config["dag_config"]
        sample_config["single-DAG"]["set_number"] = 1
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))
```

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_cli.py::TestAlgorithmSelection -v
```
Expected: FAIL (nfj test passes by accident; no config reading; algorithm is hardcoded)

**Step 3: Implement the fix**

In `src/daggen-cli.py`, read the algorithm from config and pass it through `DAG.gen()`:

In the single-DAG loop (around line 85), replace:
```python
G.gen_rnd(parallelism=dag_config["parallelism"],
          layer_num_min=dag_config["layer_num_min"],
          layer_num_max=dag_config["layer_num_max"],
          connect_prob=dag_config["connect_prob"])
```
With:
```python
algorithm = dag_config.get("algorithm", "rnd")
if algorithm == "rnd":
    G.gen_rnd(parallelism=dag_config["parallelism"],
              layer_num_min=dag_config["layer_num_min"],
              layer_num_max=dag_config["layer_num_max"],
              connect_prob=dag_config["connect_prob"])
else:
    G.gen(algorithm)
```

Do the same in the multi-DAG loop (around line 159).

In `config.json`, add `"algorithm": "rnd"` to `dag_config`:
```json
"dag_config": {
    "algorithm": "rnd",
    "parallelism": 5,
    ...
}
```

In `tests/conftest.py`, add `"algorithm": "rnd"` to `dag_config` in `sample_config`.

**Step 4: Run tests**

```bash
conda run -n dag-gen-rnd pytest tests/test_cli.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/daggen-cli.py config.json tests/conftest.py tests/test_cli.py
git commit -m "feat: make DAG generation algorithm configurable via dag_config.algorithm"
```

---

## Task 8: Compute `DAG.L` (critical path length)

**Files:**
- Modify: `src/rnddag.py`
- Test: `tests/test_rnddag.py`

**Problem:** `DAG.L` is initialized to -1 and never set. Critical path length is a key scheduling parameter.

**Step 1: Write the failing test**

In `tests/test_rnddag.py`, add to `TestGenRnd`:

```python
def test_critical_path_computed(self):
    """DAG.L should be set to the longest path length after generation."""
    assert self.dag.L >= 0
    # L is the number of edges on the longest path
    assert self.dag.L == nx.dag_longest_path_length(self.G)
```

Add the same to `TestGenNfj` and `TestGenRndLegacy`.

**Step 2: Run test to verify it fails**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestGenRnd::test_critical_path_computed -v
```
Expected: FAIL (`self.dag.L == -1`)

**Step 3: Implement the fix**

In `src/rnddag.py`, at the end of each generation method, before `self.G = G`, add:

```python
self.L = nx.dag_longest_path_length(G)
self.G = G
```

Do this for `gen_rnd()`, `gen_rnd_legacy()`, and `gen_nfj()`.

**Step 4: Run tests**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/rnddag.py tests/test_rnddag.py
git commit -m "feat: compute critical path length (DAG.L) after graph generation"
```

---

## Task 9: Fix `save_png=False` missing test

**Files:**
- Test: `tests/test_rnddag.py`

**Problem:** The `save_png` parameter added recently is untested.

**Step 1: Add the test**

In `tests/test_rnddag.py`, add to `TestSave`:

```python
def test_save_no_png(self, tmp_path):
    """save_png=False should skip PNG but still write gml and gpickle."""
    random.seed(42)
    d = DAG(i=2)
    d.gen_rnd()
    d.save(basefolder=str(tmp_path), save_png=False)

    assert not (tmp_path / "Tau_2.png").exists()
    assert (tmp_path / "Tau_2.gpickle").exists()
    assert (tmp_path / "Tau_2.gml").exists()
```

**Step 2: Run test**

```bash
conda run -n dag-gen-rnd pytest tests/test_rnddag.py::TestSave::test_save_no_png -v
```
Expected: PASS (this should already work; the test just confirms it)

**Step 3: Commit**

```bash
git add tests/test_rnddag.py
git commit -m "test: verify save_png=False skips PNG output"
```

---

## Task 10: Fix minor code quality issues

**Files:**
- Modify: `src/daggen-cli.py`
- Modify: `tests/test_utility.py`

**Problem A:** `period_set = [(x) for x in period_set]` (line ~130) is a no-op.
**Problem B:** `w_p` accumulation loop should use `sum()` (lines ~171-173).
**Problem C:** Unused `requires_pygraphviz` marker in `test_utility.py`.

**Step 1: Fix the CLI**

In `src/daggen-cli.py`:

Replace:
```python
period_set = config["multi-DAG"]["periods"]
period_set = [(x) for x in period_set]
```
With:
```python
period_set = config["multi-DAG"]["periods"]
```

Replace:
```python
w_p = 0
for item in c_.items():
    w_p = w_p + item[1]
```
With:
```python
w_p = sum(c_.values())
```

**Step 2: Fix test_utility.py**

In `tests/test_utility.py`, remove the unused `requires_pygraphviz` definition (lines 7-10):
```python
# REMOVE these lines:
requires_pygraphviz = pytest.mark.skipif(
    not pytest.importorskip("pygraphviz", reason="pygraphviz not installed"),
    reason="pygraphviz not installed"
)
```

**Step 3: Run tests**

```bash
conda run -n dag-gen-rnd pytest -v
```
Expected: All tests pass

**Step 4: Commit**

```bash
git add src/daggen-cli.py tests/test_utility.py
git commit -m "refactor: remove no-op list comprehension, simplify sum, remove unused marker"
```

---

## Task 11: Fix `utility.load_task()` to use node attributes

**Files:**
- Modify: `src/utility.py`
- Test: `tests/test_utility.py`

**Problem:** `load_task()` reconstructs `C_dict` from edge labels (which store source node's C), then hardcodes `C_dict[max_key] = 1` for the sink. The node `'C'` attribute is already stored by the generator and is the authoritative source. The edge-based reconstruction also misses isolated nodes (those with no outgoing edges other than the sink).

**Step 1: Write the failing test**

In `tests/test_utility.py`, add to `TestLoadTask`:

```python
def test_c_dict_matches_node_attributes(self, saved_dag):
    """C_dict from load_task should match the 'C' node attributes stored by generator."""
    from utility import load_task
    import networkx as nx
    folder, dag = saved_dag
    G_dict, V_array, C_dict, C_array, T, W = load_task(task_idx=0, dag_base_folder=folder)
    G = dag.get_graph()
    for node in G.nodes():
        if 'C' in G.nodes[node]:
            assert C_dict.get(node) == G.nodes[node]['C'], \
                f"Node {node}: C_dict={C_dict.get(node)}, attr={G.nodes[node]['C']}"
```

**Step 2: Run test**

```bash
conda run -n dag-gen-rnd pytest tests/test_utility.py::TestLoadTask::test_c_dict_matches_node_attributes -v
```
Expected: FAIL (sink node has `C_dict[sink]=1` hardcoded, but node attribute may differ)

**Step 3: Implement the fix**

Rewrite `load_task()` in `src/utility.py` to build `C_dict` from node attributes:

```python
def load_task(task_idx, dag_base_folder=None):
    if dag_base_folder is None:
        dag_base_folder = os.path.join(os.path.dirname(__file__), os.pardir, "data")

    dag_task_file = os.path.join(dag_base_folder, "Tau_{:d}.gpickle".format(task_idx))

    try:
        G = nx.read_gpickle(dag_task_file)
    except AttributeError:
        import pickle
        with open(dag_task_file, 'rb') as f:
            G = pickle.load(f)

    T = G.graph["T"]
    V_array = sorted(G.nodes())

    # Build adjacency dict
    G_dict = {n: [] for n in V_array}
    for u, v in G.edges():
        G_dict[u].append(v)

    # Build C_dict from node 'C' attributes (primary source of truth)
    C_dict = {}
    for n in V_array:
        node_data = G.nodes[n]
        if 'C' in node_data:
            C_dict[n] = node_data['C']
        else:
            # Fallback: read from incoming edge label (legacy files)
            for pred in G.predecessors(n):
                edge_data = G.edges[pred, n]
                if 'label' in edge_data:
                    C_dict[n] = edge_data['label']
                    break

    C_array = [C_dict[n] for n in sorted(C_dict)]
    W = sum(C_array)

    return G_dict, V_array, C_dict, C_array, T, W
```

**Step 4: Run tests**

```bash
conda run -n dag-gen-rnd pytest tests/test_utility.py -v
```
Expected: All PASS

**Step 5: Commit**

```bash
git add src/utility.py tests/test_utility.py
git commit -m "fix: load_task reads C from node attributes, falls back to edge labels"
```

---

## Final: Run all tests

```bash
conda run -n dag-gen-rnd pytest -v
```
Expected: All tests pass (or pygraphviz tests skipped if not installed).
