# Randomized DAG Generator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

Randomized Direct Acyclic Graph generator (rnd-dag-gen) for scheduling and allocation research. rnd-dag-gen supports both command line and graphical user interface. This generator is configurable through a json file and is highly extensible.


---

## Requirements

- Python >= 3.5
- NetworkX >= 2.4
- Matplotlib >= 3.1.3
- pygraphviz >= 1.5
- numpy >= 1.17

---

## Installation

Install depedencies using apt:

`$ sudo apt install python3-dev graphviz libgraphviz-dev pkg-config`

and then install Python depedencies through `requirements.txt`:

`$ pip3 install -r requirements.txt`

(Optional) To use GUI, install Qt5 for python:

`$ sudo apt install python3-pyqt5`

---

## Configuration

Use the configuration file `config.json` to configure parameters.

---

## Usage

### 1. Command line tool

`$ python3 daggen.py`


### 2. Graphic user interface

`$ python3 daggen-gui.py`

---

## Citation

Please use the following to cite this work: "Xiaotian Dai. rnd-dag-gen: A Randomized DAG Generator. https://github.com/automaticdai/rnd-dag-gen".

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

