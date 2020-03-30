# Randomized DAG Generator

A randomized Direct Acyclic Graph (DAG) generator for scheduling and allocation research. Supports both command line and graphical user interface. Configurable and extensible.

---

## 0. Requirements

- Python > 3.5
- NetworkX >= 2.4
- Matplotlib >= 3.1.3
- pygraphviz >= 1.5


## 1. Install

`sudo apt-get install python3-dev graphviz libgraphviz-dev pkg-config`

`sudo apt-get install python3-pyqt5`

and then:

`pip3 install -r requirements.txt`


## 2. Configure

Use the configuration file `config.json` to configure parameters.


## 3. Usage

### 3.1 Graphic user interface

`python3 daggen.py`

### 3.2 Command line tool

DAG generate:

`python3 daggen-cmd.py param`

DAG visualization:

`python3 dagviz.py param`


## 4. Citation

Please use the following for citation: "Xiaotian Dai. rnd-dag-gen: A Randomized DAG Generator. https://github.com/automaticdai/rnd-dag-gen".
