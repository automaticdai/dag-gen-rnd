# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Randomised Multi-DAG Task Generator for scheduling and allocation research in parallel/multi-core computing. Pure Python project (no build step). Generates Directed Acyclic Graphs with real-time task scheduling properties (periods, utilizations, execution times).

## Environment Setup

```bash
# Conda environment (recommended)
conda activate dag-gen-rnd

# Or manual install:
sudo apt install python3-dev graphviz libgraphviz-dev pkg-config
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest
```

## Commands

```bash
# Generate DAGs (main entry point)
python3 src/daggen-cli.py
python3 src/daggen-cli.py --config /path/to/config.json

# GUI (requires PyQt5)
python3 src/daggen-gui.py

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_generator.py
pytest tests/test_rnddag.py::TestGenRnd::test_produces_dag

# Run example/test script (NetworkX tutorial, not actual tests)
python3 src/test.py
```

Tests that require `pygraphviz` (save/load round-trips, CLI end-to-end with file output) are automatically skipped if the library is not installed.

## Architecture

```
config.json → daggen-cli.py → generator.py (utilization/period generation)
                             → rnddag.py   (DAG structure generation)
                             → output: data/ (GML, GPPickle, PNG)
```

**`src/rnddag.py`** — Core module. `DAG` class wraps a NetworkX DiGraph. Three generation algorithms:
- `gen_rnd()` — Layer-by-layer randomized (recommended, default)
- `gen_nfj()` — Nested fork-join
- `gen_rnd_legacy()` — Legacy randomized

`DAGTaskset` holds multiple `DAG` instances for multi-DAG mode.

**`src/generator.py`** — Scheduling parameter generation:
- `uunifast_discard()` — UUniFast-discard utilization distribution
- `drs_gen()` — DRS (Dirichlet-Rescale) utilization generation (requires `drs` package)
- `gen_period()` — Period selection from discrete population
- `gen_execution_times()` — Distributes workload across DAG nodes

**`src/daggen-cli.py`** — CLI entry point. `main(config_path, data_path)` function is importable for testing. Reads `config.json`, supports single-DAG and multi-DAG modes. Outputs to `data/` and `logs/` directories.

**`src/utility.py`** — API for loading generated DAGs from disk for downstream use.

**`src/daggen-gui.py`** — PyQt5 GUI. Supports algorithm selection, parameter input, config load/save, and DAG image display. Mixed-criticality and conditional DAG options are disabled (not yet implemented in core).

## Configuration

All generation parameters are in `config.json`. Key sections:
- `misc`: mode selection (multi-DAG vs single), core count, random seed
- `multi_task`: taskset count, tasks per set, total utilization, period options
- `single_task`: set count, workload per DAG
- `dag_config`: parallelism (max nodes/layer), layer count range, connection probability

Output format is documented in `taskset.json` (example output with nodes, edges, periods, workloads).

## Dependencies

Python 3.7+, numpy, networkx, matplotlib, pygraphviz, tqdm. pygraphviz requires graphviz system libraries.
