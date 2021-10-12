# Randomized DAG Generator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

Randomized multiple Direct Acyclic Graph generator (multi-DAG) for scheduling and allocation research. 
The `dag-gen-rnd` supports both command line and graphical user interface (GUI). This generator is configurable through a json file and is highly extensible to other purposes.


---

## Requirements

- Python >= 3.5
- NetworkX >= 2.4
- Matplotlib >= 3.1.3
- pygraphviz >= 1.5
- numpy >= 1.17

---

## Installation on Linux

Install depedencies using apt:

`$ sudo apt install python3-dev graphviz libgraphviz-dev pkg-config`

and then install Python depedencies through `requirements.txt`:

`$ pip3 install -r requirements.txt`

(Optional) To use the GUI, you need to install Qt5 for python:

`$ sudo apt install python3-pyqt5`

---

## Configuration

Use the configuration file `config.json` to configure parameters.

Generation algorithms:
- NFJ: Nested fork join
- rnd: Standard randomized DAG
- rnd_legacy (default)

---

## Usage

First, change the configurations in `config.json`. Then, depending on your perference:

### 1. Use the command line interface

`$ python3 src/daggen-cli.py`


### 2. Use the graphic user interface (development in process)

`$ python3 src/daggen-gui.py`

---

## Citation

To cite this work, please use the following format: 

"Xiaotian Dai. dag-gen-rnd: A randomized DAG generator for scheduling and allocation research. Access at https://github.com/automaticdai/dag-gen-rnd."

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
