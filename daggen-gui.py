#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

import os, logging

import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QSlider, QFormLayout, QMessageBox, QComboBox,
                             QLineEdit, QCheckBox)

from random import seed, randint, random

class GUI:
    def __init__(self):
        # create application
        app = QApplication([])

        # create widgets
        label = QLabel("MOCHA::Randomised DAG Generator")

        opt_alogrithm = QComboBox()
        opt_alogrithm.addItem("Default")

        check_conditional = QCheckBox()

        edit_crit = QLineEdit()
        edit_parallism = QLineEdit()
        edit_critical_max = QLineEdit()
        edit_critical_min = QLineEdit()
        edit_pc = QLineEdit()

        #slider_pc = QSlider(Qt.Horizontal)
        #slider_pc.setRange(0, 100)

        button_gen = QPushButton('Generate')

        # create layout
        formLayout = QFormLayout()
        formLayout.addRow(label)

        formLayout.addRow("&Algorithm:", opt_alogrithm)
        formLayout.addRow("&Maximum Parallelism <font color='blue'>>=1</font>:", edit_parallism)
        formLayout.addRow("Critical Path (min) <font color='blue'>>=3</font>:", edit_critical_min)
        formLayout.addRow("Critical Path (max) <font color='blue'>>=3</font>:", edit_critical_max)
        formLayout.addRow("p(Connnection) <font color='blue'>[0,1]</font>:", edit_pc)
        formLayout.addRow("&Conditional DAG?", check_conditional)

        formLayout.addRow(button_gen)

        # set some default values
        edit_parallism.setText("4")
        edit_critical_max.setText("7")
        edit_critical_min.setText("3")
        edit_pc.setText("0.5")

        # create window
        window = QWidget()
        window.setLayout(formLayout)
        window.show()

        # set signal / slots
        button_gen.clicked.connect(self.event_on_button_gen_clicked)

        # stary application
        app.exec_()


    def event_on_button_gen_clicked(self):
        G = dag_gen()
        dag_plot(G)
        dag_save(G)


# parameters (default)
rnd_seed = randint(1, 1000)
parallelism = 4
layer_num_min = 3 # critical path
layer_num_max = 7  # critical path
connect_prob = 0.5


def dag_gen():
    # data structures
    nodes = []          # nodes in all layers (in form of shape decomposition)
    nodes_parent = []   # nodes that can be parents
    nodes_parent_childless = []  # nodes without child
    nodes_orphan = []   # nodes without any parent

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

    # random and remove the source and the sink node
    layer_num_this = randint(layer_num_min - 2, layer_num_max - 2)

    # generate layer by layer
    for k in range(layer_num_this):
        # randomised nodes in each layer
        m = randint(1, parallelism)

        nodes_t = []
        for j in range(m):
            nodes_t.append(n)
            nodes_orphan.append(n)
            G.add_node(n, rank=k+1)
            n = n + 1

        nodes.append(nodes_t)

        # initially assume all parents are childless
        nodes_parent_childless[:] = nodes_parent_childless[:] + nodes_parent[:]

        # iterates all nodes in the current layout
        for i in nodes[k+1]:
            for ii in nodes_parent:
                # add connections
                if random() < connect_prob:
                    G.add_edge(ii, i)
                    if i in nodes_orphan:
                        nodes_orphan.remove(i)
                    if ii in nodes_parent_childless:
                        nodes_parent_childless.remove(ii)
        # add all childs as candidate parents for the next layer
        nodes_parent[:] = nodes[k+1]

        # connect all orphan to the root node
        for i in nodes_orphan:
            nodes_orphan.remove(i)
            G.add_edge(1, i)
            # if i in nodes_parent:
            #     nodes_parent.remove(i)

    # Dealing with the final layer
    # connect everything together to a final node
    for i in nodes_parent:
        G.add_edge(i, n)

    for i in nodes_parent_childless:
        G.add_edge(i, n)

    # connect all orphan to the root node
    for i in nodes_orphan:
        nodes_orphan.remove(i)
        G.add_edge(1, i)

    # mutate a node to be conditional
    # G.add_node('2', style='filled', fillcolor='red', shape='diamond')

    # handling critical Path


    # set graph properties

    print(nodes)
    #print(nodes_orphan)

    # return the graph
    return G


def dag_plot(G):
    # layout graph
    #A = to_agraph(G)
    A = nx.nx_agraph.to_agraph(G)
    print(A)
    print(type(A))
    A.layout('dot')

    # plot graph
    filename = 'output/graph.png'
    A.draw(filename, format="png")

    img = mpimg.imread(filename)
    ypixels, xpixels, bands = img.shape
    dpi = 100.
    xinch = xpixels / dpi
    yinch = ypixels / dpi

    # plot and save in the same size as the original
    plt.figure(figsize=(xinch, yinch))
    ax = plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
    ax.imshow(img, interpolation='none')

    # plt.show(block=False)
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
    gui = GUI()

    # for test only
    #event_on_button_gen_clicked()
    #plt.show()
