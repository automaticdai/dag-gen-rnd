# Randomised Multi-DAG Task Generator for Scheduling and Allocation

![](docs/dag-gen-rnd-banner.png)


![](https://img.shields.io/github/stars/automaticdai/dag-gen-rnd)
![](https://img.shields.io/github/forks/automaticdai/dag-gen-rnd)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

The **dag-gen-rnd** is a randomised multiple Directed Acyclic Graph (DAG) task generator designed for scheduling and allocation research in parallel and multi-core computing. 
**dag-gen-rnd** supports both command line (`daggen-cli`) and graphical user interface (`daggen-gui`). This generator can be easily configured through a `.json` file and is highly extensible for other purposes.

Support the following DAG generation algorithms:

- `nfj`: Nested fork-join
- `rnd`: standard randomised DAG (layer-by-layer / LBL)
- `rnd_legacy`: default randomised DAG

Supported utilisation generation algorithms:

- `UUniFast` [1]
- `UUniFast-discard` [2]
- `DRS`: The Dirichlet-Rescale (DRS) algorithm [3]

References:  

- [1] Bini, Enrico, and Giorgio C. Buttazzo. "Measuring the performance of schedulability tests." Real-Time Systems 30, no. 1 (2005): 129-154.  
- [2] Davis, Robert I., and Alan Burns. "Improved priority assignment for global fixed priority pre-emptive scheduling in multiprocessor real-time systems." Real-Time Systems 47, no. 1 (2011): 1-40.  
- [3] Griffin, David, Iain Bate, and Robert I. Davis. "Generating utilization vectors for the systematic evaluation of schedulability tests." In 2020 IEEE Real-Time Systems Symposium (RTSS), pp. 76-88. IEEE, 2020.

---

## Requirements

- `Python >= 3.11`
- `NetworkX >= 2.4`
- `Matplotlib >= 3.1.3`
- `pygraphviz >= 1.5`
- `numpy == 2.1`
- `tqdm >= 4.45.0`
- `pyqt5 >= 5.12`
- `drs >= 2.0`
- `zipp == 3.19.1`

---

## Installation on Linux

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

Install system dependencies with apt:

`$ sudo apt install python3-dev graphviz libgraphviz-dev pkg-config libxcb-xinerama0 libxcb-cursor0`

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then sync the environment:

```
$ uv sync                # runtime dependencies
$ uv sync --group dev    # include pytest for running tests
```

Run commands inside the managed environment with `uv run`, e.g. `uv run python src/daggen-cli.py` or `uv run pytest`.

---

## Configuration

Use the configuration file `config.json` to configure parameters.

### Global Settings

Parameters in the `global` section apply to all generation modes:

- `multi-DAG_on`: `true` for multi-DAG mode, `false` for single-DAG mode
- `cores`: number of processor cores (used in multi-DAG mode)
- `print_DAG`: print node/edge data to stdout during generation
- `save_to_file`: save generated DAGs to the `data/` directory (GML, GPPickle, and optionally PNG)
- `save_png`: save a PNG image of each DAG (default: `true`); set to `false` to skip PNG generation and save disk space
- `dummy_source_and_sink`: add dummy source and sink nodes to each DAG
- `rnd_seed`: random seed for reproducibility
- `util_algorithm`: utilization generation algorithm (see [Utilization Algorithm](#utilization-algorithm))

### Single DAG

To generate a single DAG task, set `multi-DAG_on=false`, then in `single-DAG`:

- `multi-DAG_on`: false
- `set_number`: number of tasksets
- `workload`: sum(C_i)

### Multiple DAGs

To generate a multi-DAG taskset, set `multi-DAG_on=true`, then in `multi-DAG`:

- `set_number`: number of tasksets
- `utilization`: total utilisation
- `task_number_per_set`: number of tasks in each taskset
- `periods`: period set candidates

### Utilization Algorithm

Set `util_algorithm` in `global` to choose the utilization generation algorithm for multi-DAG mode:

- `"uunifast_discard"` (default): UUniFast-discard [2]
- `"drs"`: Dirichlet-Rescale [3]

---

## Usage

### Use the CLI (`daggen-cli`)

First, change the configurations in `config.json`. Then, run the command line interface:

`$ uv run python src/daggen-cli.py`


### Use the GUI (`daggen-gui`)

`$ uv run python src/daggen-gui.py`

To use the generated DAGs, see the provided API in `utility.py` which also gives an example.

---

## Examples

Here are some simple examples of generated DAGs:

|![](docs/example_1.png)|![](docs/example_2.png)|![](docs/example_3.png)|
|--|--|--|

or more complicated DAGs that can also be generated:

|![](docs/example_4.png)|![](docs/example_5.png)|
|--|--|

---

## Known Issues

1. In some cases, the workload of the critical path could be larger than the period. The generator does not prohibit this case as this is not treated as a bug (as you can distribute the workload to multiple cores). The users need to be aware of this and deal with them in their favourite way, e.g. discarding.

---

## Academic Use of the Generator

The generator is featured in multiple academic papers:

1. Shuai Zhao, Xiaotian Dai, Iain Bate, Alan Burns, Wanli Chang. "DAG scheduling and analysis on multiprocessor systems: Exploitation of parallelism and dependency." In Real-Time Systems Symposium (RTSS), pp. 128-140. IEEE, 2020.
1. Shuai Zhao, Xiaotian Dai, Iain Bate. "DAG Scheduling and Analysis on Multi-core Systems by Modelling Parallelism and Dependency." Transactions on Parallel and Distributed Systems (TPDS). IEEE, 2022. 
1. Yani Ping, Kun Xie, Xiaohong Huang, Chengcheng Li, and Yasheng Zhang. "GNN-Based QoE Optimization for Dependent Task Scheduling in Edge-Cloud Computing Network." In 2024 IEEE Wireless Communications and Networking Conference (WCNC), pp. 1-6. IEEE, 2024.
1. Yuanhai Zhang, Shuai Zhao, Gang Chen, and Kai Huang. "Fault-tolerant DAG scheduling with runtime reconfiguration on multicore real-time systems." In 2024 IEEE 35th International Conference on Application-specific Systems, Architectures and Processors (ASAP), pp. 19-27. IEEE, 2024.
1. Hong Kang, Minghao Li, Lehao Lin, Sizheng Fan, and Wei Cai. "Bridging Incentives and Dependencies: An Iterative Combinatorial Auction Approach to Dependency-Aware Offloading in Mobile Edge Computing." IEEE Transactions on Mobile Computing, 2024.
1. Tommaso Cucinotta, Alexandre Amory, Gabriele Ara, Francesco Paladino, and Marco Di Natale. "Multi-criteria optimization of real-time DAGs on heterogeneous platforms under p-EDF." ACM Transactions on Embedded Computing Systems 23, no. 1, 2024.
1. Abigail Eisenklam, Robert Gifford, Georgiy A. Bondar, Yifan Cai, Tushar Sial, Linh Thi Xuan Phan, and Abhishek Halder. "Rasco: Resource Allocation and Scheduling Co-design for DAG Applications on Multicore." ACM Transactions on Embedded Computing Systems 24, no. 5s, 2025.
1. Yuanhai Zhang, Shuai Zhao, and Kai Huang. "DAG Scheduling and Analysis in Multicore Real-Time Systems via Sub-Graph Division." IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, 2026.

---

## Citation

Please cite the following paper if you use this software in your research: 

```
Shuai Zhao, Xiaotian Dai, Iain Bate, Alan Burns, Wanli Chang. "DAG scheduling and analysis on multiprocessor systems: Exploitation of parallelism and dependency". In Real-Time Systems Symposium (RTSS), pp. 128-140. IEEE, 2020.
```

BibTex:

```
@inproceedings{zhao2020dag,
  title={DAG scheduling and analysis on multiprocessor systems: Exploitation of parallelism and dependency},
  author={Zhao, Shuai and Dai, Xiaotian and Bate, Iain and Burns, Alan and Chang, Wanli},
  booktitle={2020 IEEE Real-Time Systems Symposium (RTSS)},
  pages={128--140},
  year={2020},
  organization={IEEE}
}
```

Alternatively, if you just want to cite the software:

```
Xiaotian Dai. (2022). dag-gen-rnd: A randomised multi-DAG task generator for scheduling and allocation research (v0.1). Zenodo. https://doi.org/10.5281/zenodo.6334205
```

BibTex:

```
@software{xiaotian_dai_2022_6334205,
  author       = {Xiaotian Dai},
  title        = {{dag-gen-rnd: A randomised multi-DAG task generator 
                   for scheduling and allocation research}},
  month        = mar,
  year         = 2022,
  publisher    = {Zenodo},
  version      = {v0.1},
  doi          = {10.5281/zenodo.6334205},
  url          = {https://doi.org/10.5281/zenodo.6334205}
}
```

---

## License

This software is licensed under MIT. See [LICENSE](LICENSE) for details.

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
