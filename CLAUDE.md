# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Randomised Multi-DAG Task Generator for scheduling and allocation research in parallel/multi-core computing. Pure Python project (no build step). Generates Directed Acyclic Graphs with real-time task scheduling properties (periods, utilizations, execution times).

## Environment Setup

```bash
# System libs (one-time)
sudo apt install python3-dev graphviz libgraphviz-dev pkg-config

# Python env managed by uv
uv sync                # runtime deps
uv sync --group dev    # include pytest
```

## Commands

```bash
# Generate DAGs (main entry point)
uv run python src/daggen-cli.py
uv run python src/daggen-cli.py --config /path/to/config.json

# GUI (requires PyQt5)
uv run python src/daggen-gui.py

# Run all tests
uv run pytest

# Run a single test file or test
uv run pytest tests/test_generator.py
uv run pytest tests/test_rnddag.py::TestGenRnd::test_produces_dag
```

Tests that require `pygraphviz` (save/load round-trips, CLI end-to-end with file output) are automatically skipped if the library is not installed.

## Architecture

```
config.json → daggen-cli.py → dag_factory.py (shared generation orchestration)
                             → generator.py  (utilization/period generation)
                             → rnddag.py     (DAG structure generation)
                             → output: data/ (GML, GPPickle, PNG)
```

**`src/rnddag.py`** — Core module. `DAG` class wraps a NetworkX DiGraph. Three generation algorithms:
- `gen_rnd()` — Layer-by-layer randomized (recommended, default)
- `gen_nfj()` — Nested fork-join
- `gen_rnd_legacy()` — Legacy randomized

**`src/generator.py`** — Scheduling parameter generation:
- `uunifast_discard()` — UUniFast-discard utilization distribution
- `drs_gen()` — DRS (Dirichlet-Rescale) utilization generation (requires `drs` package)
- `gen_period()` — Period selection from discrete population
- `gen_execution_times()` — Distributes workload across DAG nodes

**`src/dag_factory.py`** — Shared generation orchestration:
- `generate_dag()` — Creates a single DAG with structure and execution times applied
- `generate_multi_dag_taskset()` — Generator yielding `(set_index, task_index, DAG, c_dict)` tuples

**`src/daggen-cli.py`** — CLI entry point. `main(config_path, data_path)` function is importable for testing. Reads `config.json`, supports single-DAG and multi-DAG modes. Outputs to `data/` and `logs/` directories.

**`src/utility.py`** — API for loading generated DAGs from disk for downstream use.

**`src/daggen-gui.py`** — PyQt5 GUI (`DagGenGUI` class). Supports algorithm selection, parameter input, config load/save, and DAG image display.

## Configuration

All generation parameters are in `config.json`. Key sections:
- `misc`: mode selection (multi-DAG vs single), core count, random seed
- `multi-DAG`: taskset count, tasks per set, total utilization, period options
- `single-DAG`: set count, workload per DAG
- `dag_config`: parallelism (max nodes/layer), layer count range, connection probability

Output format is documented in `taskset.json` (example output with nodes, edges, periods, workloads).

## Dependencies

Python 3.11+, numpy, networkx, matplotlib, pygraphviz, tqdm. Declared in `pyproject.toml` (managed with `uv`). pygraphviz requires graphviz system libraries.
