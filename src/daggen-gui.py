#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

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

import rnddag


class GUI:
    def __init__(self):
        # create application
        app = QApplication([])

        # load default configuration


        # create widgets
        # myFont = Qt.QFont()
        # myFont.setBold(True)
        # self.label.setFont(myFont)

        label = QLabel("dag-gen-rnd: Randomised DAG Generator")

        opt_alogrithm = QComboBox()
        opt_alogrithm.addItem("Default")
        opt_alogrithm.addItem("Nested-Fork Join (NFJ)")

        check_conditional = QCheckBox()
        check_mcs_dag = QCheckBox()

        edit_crit = QLineEdit()
        edit_parallism = QLineEdit()
        edit_critical_max = QLineEdit()
        edit_critical_min = QLineEdit()
        edit_pc = QLineEdit()

        #slider_pc = QSlider(Qt.Horizontal)
        #slider_pc.setRange(0, 100)

        button_gen_conf = QPushButton('Generate Configuration')
        button_gen = QPushButton('Generate DAGs')

        # create layout
        formLayout = QFormLayout()
        formLayout.addRow(label)

        formLayout.addRow("&Algorithm:", opt_alogrithm)
        formLayout.addRow("&Maximum Parallelism <font color='blue'>>=1</font>:", edit_parallism)
        formLayout.addRow("Critical Path (min) <font color='blue'>>=3</font>:", edit_critical_min)
        formLayout.addRow("Critical Path (max) <font color='blue'>>=3</font>:", edit_critical_max)
        formLayout.addRow("p(Connnection) <font color='blue'>[0,1]</font>:", edit_pc)
        formLayout.addRow("&Mixed-Criticality DAG?", check_mcs_dag)
        formLayout.addRow("&Conditional DAG?", check_conditional)

        formLayout.addRow(button_gen_conf)
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
        G = rnddag.gen()
        rnddag.plot(G)
        rnddag.save(G)


# Main function
if __name__ == "__main__":
    # load configurations
    #with open('config.json', 'r') as f:
    #    array = json.load(f)

    # fix random seed
    # seed(rnd_seed)

    #print(array["tg"])

    # initialize the GUI
    gui = GUI()

    # for test only
    #event_on_button_gen_clicked()
    #plt.show()
