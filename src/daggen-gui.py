#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import os, logging

import sys
import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QApplication, QStatusBar, QWidget, QLabel,
                             QPushButton, QSlider, QFormLayout, QMessageBox, 
                             QComboBox, QLineEdit, QCheckBox, QMenu, QAction)

from random import seed, randint, random

import rnddag


class daggen_gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # config menu
        menubar = self.menuBar()

        loadAct = QAction('Load Config', self)
        saveAct = QAction('Save Config', self)

        fileMenu = menubar.addMenu('File')

        impMenu = QMenu('Import', self)
        impAct = QAction('Import from file', self)
        impMenu.addAction(impAct)

        quitExt = QAction('Quit', self)

        fileMenu.addAction(loadAct)
        fileMenu.addAction(saveAct)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(quitExt)

        # config status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # config UI layout
        self.gui()

        # start the window
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle('dag-gen-rnd: Randomised DAG Generator')
        self.show()

    def gui(self):
        # create widgets
        # myFont = Qt.QFont()
        # myFont.setBold(True)
        # self.label.setFont(myFont)

        label = QLabel("Parameter Configurations:")

        opt_alogrithm = QComboBox()
        opt_alogrithm.addItem("Default (rnd)")
        opt_alogrithm.addItem("Nested-Fork Join (nfj)")

        check_conditional = QCheckBox()
        check_mcs_dag = QCheckBox()

        edit_crit = QLineEdit()
        edit_parallism = QLineEdit()
        edit_critical_max = QLineEdit()
        edit_critical_min = QLineEdit()
        edit_pc = QLineEdit()
        edit_mcs = QLineEdit()

        # slider_pc = QSlider(Qt.Horizontal)
        # slider_pc.setRange(0, 100)

        button_gen_conf = QPushButton('Generate Configuration')
        button_gen = QPushButton('Generate DAGs')

        # create layout
        formLayout = QFormLayout()
        formLayout.addRow(label)

        formLayout.addRow("&Algorithm:", opt_alogrithm)
        formLayout.addRow("&Maximum parallelism <font color='blue'>>=1</font>:", edit_parallism)
        formLayout.addRow("Min critical path length <font color='blue'>>=3</font>:", edit_critical_min)
        formLayout.addRow("Max critical path length <font color='blue'>>=3</font>:", edit_critical_max)
        formLayout.addRow("p(Connnection) <font color='blue'>[0,1]</font>:", edit_pc)
        formLayout.addRow("&Mixed-criticality DAG?", check_mcs_dag)
        formLayout.addRow("&Conditional DAG?", check_conditional)

        formLayout.addRow(button_gen_conf)
        formLayout.addRow(button_gen)

        # set some default values
        edit_parallism.setText("4")
        edit_critical_max.setText("7")
        edit_critical_min.setText("3")
        edit_pc.setText("0.5")
        edit_mcs.setText("0.5")

        # set signal / slots
        button_gen.clicked.connect(self.event_on_button_gen_clicked)

        # create widget in the main window
        widget = QWidget()
        widget.setLayout(formLayout)
        self.setCentralWidget(widget)

    def event_on_button_gen_clicked(self):
        G = rnddag.DAG()
        G.gen("rnd")
        G.save()
        G.plot()


# Main function
if __name__ == "__main__":
    # load configurations
    #with open('config.json', 'r') as f:
    #    array = json.load(f)

    # fix random seed
    # seed(rnd_seed)

    # initialize the GUI
    app = QApplication(sys.argv)
    win = daggen_gui()
    sys.exit(app.exec_())
