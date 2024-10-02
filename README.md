# Randomized Multi-DAG Task Generator for Scheduling and Allocation Research

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

**dag-gen-rnd** --- A randomized multiple Directed Acyclic Graph (DAG) task generator designed for scheduling and allocation research in parallel and multi-core computing. 

**dag-gen-rnd** supports both command line (`daggen-cli`) and graphical user interface (`daggen-gui`; in development). This generator can be easily configured through a `.json` file and is highly extensible for other purposes.

Support the following DAG generation algorithms:

- `nfj`: Nested fork-join
- `rnd`: standard randomized DAG (layer-by-layer)
- `rnd_legacy`: default randomized DAG

Supported utilization generation algorithms:

- UUnifast
- UUnifast-discard

---

## Requirements

- `Python >= 3.7`
- `NetworkX >= 2.4`
- `Matplotlib >= 3.1.3`
- `pygraphviz >= 1.5`
- `numpy >= 1.17`
- `tqdm >= 4.45.0`
- `pyqt5` (optional for GUI)

---

## Installation on Linux

Install dependencies using apt:

`$ sudo apt install python3-dev graphviz libgraphviz-dev pkg-config`

and then install Python depedencies through `requirements.txt`:

`$ pip3 install -r requirements.txt`

(Optional) To use the GUI, you need to install Qt5 for Python:

`$ sudo apt install python3-pyqt5`

---

## Configuration

Use the configuration file `config.json` to configure parameters.

### Single DAG

To generate single DAG task, set `multi-DAG=false`, then in `single_task`:

- `multi-DAG`: false
- `set_number`: number of tasksets
- `workload`: sum(C_i)

### Multiple DAGs

To generate multi-DAG taskset, set `multi-DAG=true`, then in `multi_task`:

- `set_number`: number of tasksets
- `utilization`: total utilization
- `task_number_per_set`: number of tasks in each taskset
- `periods`: period set candidates

---

## Usage

### Use the cli

First, change the configurations in `config.json`. Then, run the command line interface:

`$ python3 src/daggen-cli.py`


### Use the GUI (development in process)

`$ python3 src/daggen-gui.py`

To use the generated DAGs, see the provided API in `utlity.py` which also gives an example.

---

## Examples

Here are some simple examples of generated DAGs:

|![](doc/example_1.png)|![](doc/example_2.png)|![](doc/example_3.png)|
|--|--|--|

or more complicated DAGs that can also be generated:

|![](doc/example_4.png)|![](doc/example_5.png)|
|--|--|

---

## Known Issues

1. *Compatiability on Windows*: This code is tested on Linux (Ubuntu) but not on Windows. There should not be too many problems as Python is good at cross-platform. However, the only potential issue is that the difference is in folder naming where Windows uses a backslash (`\`), instead of a forwardslash (`/`). I will test it and make it compatitable in the future. 
2. In some cases, the workload of the critical path could be larger than the period. The generator does not prohibit this case as this is not treated as a bug (as you can distribute the workload to multiple cores). The users need to be aware this and deal with them in their favority way, e.g. discarding.
3. If you get an error while building pygraphviz during installing the dependencies: install graphviz with `apt install graphviz graphviz-dev`.

---

## Published papers used the generator

1. Shuai Zhao, Xiaotian Dai, Iain Bate, Alan Burns, Wanli Chang. "DAG scheduling and analysis on multiprocessor systems: Exploitation of parallelism and dependency". In Real-Time Systems Symposium (RTSS), pp. 128-140. IEEE, 2020.
2. Shuai Zhao, Xiaotian Dai, Iain Bate. "DAG Scheduling and Analysis on Multi-core Systems by Modelling Parallelism and Dependency". Transactions on Parallel and Distributed Systems (TPDS). IEEE. 2022.

---

## Citation

Please cite the following work if you use this software in your research: 

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
Xiaotian Dai. (2022). dag-gen-rnd: A randomized multi-DAG task generator for scheduling and allocation research (v0.1). Zenodo. https://doi.org/10.5281/zenodo.6334205
```

BibTex:

```
@software{xiaotian_dai_2022_6334205,
  author       = {Xiaotian Dai},
  title        = {{dag-gen-rnd: A randomized multi-DAG task generator 
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
