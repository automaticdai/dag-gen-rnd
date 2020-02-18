#!/usr/bin/python3

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

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

from random import seed, randint, random


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
    opt_alogrithm.addItem("Layer-by-layer")

    edit_crit = QLineEdit()
    edit_parallism = QLineEdit()
    edit_depth = QLineEdit()
    edit_span = QLineEdit()

    slider_pc = QSlider(Qt.Horizontal)
    slider_pc.setRange(0, 100)

    button_gen = QPushButton('Generate')

    # create layout
    formLayout = QFormLayout()
    formLayout.addRow(label)

    formLayout.addRow("&Algorithm:", opt_alogrithm)
    formLayout.addRow("&Length of critical Path", edit_crit)
    formLayout.addRow("&Max Parallism", edit_parallism)
    formLayout.addRow("&Branches of Span:", edit_span)
    formLayout.addRow("&Depth of DAG:", edit_depth)

    formLayout.addRow("P(Connnection):", slider_pc)

    formLayout.addRow(button_gen)

    # set some default values
    edit_crit.setText("[10, 100]")
    edit_parallism.setText("3")
    edit_depth.setText("5")
    edit_span.setText("2")

    slider_pc.setValue(20)

    # create window
    window = QWidget()
    window.setLayout(formLayout)
    window.show()

    # set signal / slots
    button_gen.clicked.connect(event_on_button_gen_clicked)

    # stary application
    app.exec_()


# parameters
rnd_seed = 1
parallism = 3
layer_num = 10
connect_prob = 0.9


def dag_gen():
    # data structures
    nodes = []
    nodes_parent = []
    nodes_orphan = []   # orphan is defined as a node without any parent

    edges = []

    # initial a new graph
    G = nx.DiGraph()

    # add the root node
    n = 1
    G.add_node(n, rank=0)
    nodes.append([n])
    nodes_parent.append(n)
    n = n + 1

    print(nodes)
    print(edges)

    # generate layer by layer
    for k in range(layer_num-1):
        # randomised nodes in each layer
        m = randint(1, parallism)

        nodes_t = []
        for j in range(m):
            nodes_t.append(n)
            nodes_orphan.append(n)
            G.add_node(n, rank=k+1)
            n = n + 1

        nodes.append(nodes_t)

        # iterates all nodes in the current layout
        for i in nodes[k+1]:
            print(i)
            for ii in nodes_parent:
                # add connections
                if random() < connect_prob:
                    G.add_edge(ii, i)
                    if i in nodes_orphan:
                        nodes_orphan.remove(i)
                    # if ii in nodes_orphan:
                    #     nodes_orphan.remove(ii)

        nodes_parent[:] = nodes[k+1]

    # mutate a conditional node

    # G.add_node('2', style='filled', fillcolor='red', shape='diamond')

    # set graph properties

    print(nodes)
    print(nodes_orphan)

    # how to handle orphans?

    # also what happens if an orphans has a parent but no child???

    # simplify: A->B->C to A->C

    # return the graph
    return G


def dag_plot(G):
    # layout graph
    A = to_agraph(G)
    print(A)
    A.layout('dot')

    # plot graph
    filename = 'output/abcd.png'
    A.draw(filename, format="png")

    img = mpimg.imread(filename)
    ypixels, xpixels, bands = img.shape
    dpi = 96.
    xinch = xpixels / dpi
    yinch = ypixels / dpi

    # plot and save in the same size as the original
    plt.figure(figsize=(xinch, yinch))
    ax = plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
    ax.imshow(img, interpolation='none')

    plt.show()


def dag_save(G):
    pass


# Main function
if __name__ == "__main__":
    # fix random seed
    seed(rnd_seed)

    # load configurations
    #with open('config.json', 'r') as f:
    #    array = json.load(f)

    #print(array["tg"])

    # initialize GUI
    #event_on_button_gen_clicked()

    gui_init()
