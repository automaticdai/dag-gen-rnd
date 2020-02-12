#!/usr/bin/python3

import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QSlider, QFormLayout, QMessageBox, QComboBox,
                             QLineEdit)


def event_on_button_gen_clicked():
    G = dag_gen()
    dag_plot(G)
    dag_save(G)


def gui_init():
    # create application
    app = QApplication([])

    # create widgets
    label = QLabel("Randomised DAG Generator")

    opt_alogrithm = QComboBox()
    opt_alogrithm.addItem("Default")

    edit_util = QLineEdit()
    edit_number = QLineEdit()
    edit_depth = QLineEdit()
    edit_span = QLineEdit()

    slider_pa = QSlider(Qt.Horizontal)
    slider_pb = QSlider(Qt.Horizontal)
    slider_pc = QSlider(Qt.Horizontal)
    slider_pa.setRange(0, 100)
    slider_pb.setRange(0, 100)
    slider_pc.setRange(0, 100)

    button_gen = QPushButton('Generate')

    # create layout
    formLayout = QFormLayout()
    formLayout.addRow(label)

    formLayout.addRow("&Algorithm:", opt_alogrithm)
    formLayout.addRow("&Total Utilization:", edit_util)
    formLayout.addRow("&Number of DAGs", edit_number)
    formLayout.addRow("&Branches of Span:", edit_span)
    formLayout.addRow("&Depth of DAG:", edit_depth)
    formLayout.addRow("P(Proceed):", slider_pa)
    formLayout.addRow("P(Span):", slider_pb)
    formLayout.addRow("P(Join):", slider_pc)
    formLayout.addRow(button_gen)

    # set some default values
    edit_util.setText("1.0")
    edit_number.setText("1")
    edit_depth.setText("5")
    edit_span.setText("2")

    slider_pa.setValue(50)
    slider_pb.setValue(30)
    slider_pc.setValue(20)

    # create window
    window = QWidget()
    window.setLayout(formLayout)
    window.show()

    # set signal / slots
    button_gen.clicked.connect(event_on_button_gen_clicked)

    # stary application
    app.exec_()


def dag_gen():
    # initial a new graph
    G = nx.DiGraph()

    # add nodes
    G.add_node('A', rank=0)
    G.add_nodes_from(['B', 'C', 'D'], style='filled', fillcolor='red',
                     shape='diamond')
    G.add_nodes_from(['E', 'F', 'G'])
    G.add_nodes_from(['H'], label='H')

    # add edges
    G.add_edge('A', 'B', arrowsize=2.0)
    G.add_edge('A', 'C', penwidth=2.0)
    G.add_edge('A', 'D')
    G.add_edges_from([('B', 'E'), ('B', 'F')], color='blue')
    G.add_edges_from([('C', 'E'), ('C', 'G')])
    G.add_edges_from([('D', 'F'), ('D', 'G')])
    G.add_edges_from([('E', 'H'), ('F', 'H'), ('G', 'H')])

    # set graph properties
    G.graph['graph'] = {'rankdir': 'TD'}
    G.graph['node'] = {'shape': 'circle'}
    G.graph['edges'] = {'arrowsize': '2.0'}

    return G


def dag_plot(G):
    # layout graph
    A = to_agraph(G)
    print(A)
    A.layout('dot')

    # plot graph
    filename = 'output/abcd.png'
    A.draw(filename)

    img = mpimg.imread(filename)
    plt.imshow(img)
    plt.show()


def dag_save(G):
    pass


if __name__ == "__main__":
    # load configurations
    with open('config.json', 'r') as f:
        array = json.load(f)

    print(array["tg"])

    # initialize GUI
    gui_init()
