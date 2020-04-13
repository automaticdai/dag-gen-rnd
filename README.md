# Randomized DAG Generator

A randomized Direct Acyclic Graph (DAG) generator for scheduling and allocation research. Supports both command line and graphical user interface. Configurable and extensible.


---

## Requirements

- Python > 3.5
- NetworkX >= 2.4
- Matplotlib >= 3.1.3
- pygraphviz >= 1.5
- numpy > 1.17


---

## Installation

Install depedencies using apt:

`$ sudo apt install python3-dev graphviz libgraphviz-dev pkg-config`

`$ sudo apt install python3-pyqt5`

and then install more depedencies through Python requirements:

`$ pip3 install -r requirements.txt`


---

## Configure

Use the configuration file `config.json` to configure parameters.

---

## Usage

### 1. Command line tool

DAG generate:

`$ python3 daggen.py params`


### 2. Graphic user interface

`$ python3 daggen-gui.py`


---

## Citation

Please use the following for cite this work: "Xiaotian Dai. rnd-dag-gen: A Randomized DAG Generator. https://github.com/automaticdai/rnd-dag-gen".

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 © <a href="http://fvcproductions.com" target="_blank">Xiaotian Dai</a>.

---
