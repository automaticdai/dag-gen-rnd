#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import os
import sys
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QMainWindow, QApplication, QStatusBar, QWidget, QLabel,
                             QPushButton, QFormLayout, QMessageBox, QFileDialog,
                             QComboBox, QLineEdit, QCheckBox, QMenu, QAction)

import rnddag


class daggen_gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # config menu
        menubar = self.menuBar()

        self.loadAct = QAction('Load Config', self)
        self.saveAct = QAction('Save Config', self)

        fileMenu = menubar.addMenu('File')

        impMenu = QMenu('Import', self)
        self.impAct = QAction('Import from file', self)
        impMenu.addAction(self.impAct)

        self.quitAct = QAction('Quit', self)

        fileMenu.addAction(self.loadAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addMenu(impMenu)
        fileMenu.addAction(self.quitAct)

        # connect menu actions
        self.loadAct.triggered.connect(self.load_config)
        self.saveAct.triggered.connect(self.save_config)
        self.impAct.triggered.connect(self.load_config)
        self.quitAct.triggered.connect(self.close)

        # config status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # config UI layout
        self.gui()

        # start the window
        self.setGeometry(500, 500, 520, 600)
        self.setWindowTitle('dag-gen-rnd: Randomised DAG Generator')
        self.show()

    def gui(self):
        label = QLabel("<b>Parameter Configurations:</b>")

        self.opt_algorithm = QComboBox()
        self.opt_algorithm.addItem("Default (rnd)")
        self.opt_algorithm.addItem("Random Legacy (rnd_legacy)")
        self.opt_algorithm.addItem("Nested-Fork Join (nfj)")

        self.check_conditional = QCheckBox()
        self.check_mcs_dag = QCheckBox()

        self.edit_parallelism = QLineEdit()
        self.edit_critical_max = QLineEdit()
        self.edit_critical_min = QLineEdit()
        self.edit_pc = QLineEdit()
        self.edit_mcs = QLineEdit()

        self.button_gen_conf = QPushButton('Load Default Configuration')
        self.button_gen = QPushButton('Generate DAGs')

        # DAG display area
        self.dag_display = QLabel("No DAG generated yet.")
        self.dag_display.setAlignment(Qt.AlignCenter)
        self.dag_display.setMinimumHeight(200)

        # create layout
        formLayout = QFormLayout()
        formLayout.addRow(label)

        formLayout.addRow("&Algorithm:", self.opt_algorithm)
        formLayout.addRow("&Maximum parallelism <font color='blue'>>=1</font>:", self.edit_parallelism)
        formLayout.addRow("Min critical path length <font color='blue'>>=3</font>:", self.edit_critical_min)
        formLayout.addRow("Max critical path length <font color='blue'>>=3</font>:", self.edit_critical_max)
        formLayout.addRow("p(Connection) <font color='blue'>[0,1]</font>:", self.edit_pc)
        formLayout.addRow("&Mixed-criticality DAG?", self.check_mcs_dag)
        formLayout.addRow("p(High)", self.edit_mcs)
        formLayout.addRow("&Conditional DAG?", self.check_conditional)

        formLayout.addRow(self.button_gen_conf)
        formLayout.addRow(self.button_gen)
        formLayout.addRow(self.dag_display)

        # set some default values
        self.edit_parallelism.setText("4")
        self.edit_critical_max.setText("7")
        self.edit_critical_min.setText("3")
        self.edit_pc.setText("0.5")
        self.edit_mcs.setText("0.5")

        # disable unimplemented features
        self.check_conditional.setEnabled(False)
        self.check_conditional.setToolTip("Conditional DAG support not yet implemented")
        self.check_mcs_dag.setEnabled(False)
        self.check_mcs_dag.setToolTip("Mixed-criticality DAG support not yet implemented")
        self.edit_mcs.setEnabled(False)
        self.edit_mcs.setToolTip("Mixed-criticality DAG support not yet implemented")

        # set signal / slots
        self.button_gen.clicked.connect(self.event_on_button_gen_clicked)
        self.button_gen_conf.clicked.connect(self.load_default_config)

        # create widget in the main window
        widget = QWidget()
        widget.setLayout(formLayout)
        self.setCentralWidget(widget)

    def event_on_button_gen_clicked(self):
        try:
            # read parameters from UI
            algo_text = self.opt_algorithm.currentText()
            parallelism = int(self.edit_parallelism.text())
            layer_min = int(self.edit_critical_min.text())
            layer_max = int(self.edit_critical_max.text())
            connect_prob = float(self.edit_pc.text())

            # validate
            if parallelism < 1:
                raise ValueError("Parallelism must be >= 1")
            if layer_min < 3:
                raise ValueError("Min critical path length must be >= 3")
            if layer_max < layer_min:
                raise ValueError("Max must be >= Min critical path length")
            if not (0.0 <= connect_prob <= 1.0):
                raise ValueError("Connection probability must be in [0, 1]")

            # map algorithm selection
            if "rnd_legacy" in algo_text:
                algorithm = "legacy"
            elif "nfj" in algo_text:
                algorithm = "nfj"
            else:
                algorithm = "rnd"

            # generate DAG
            G = rnddag.DAG()
            if algorithm == "rnd":
                G.gen_rnd(parallelism=parallelism,
                          layer_num_min=layer_min,
                          layer_num_max=layer_max,
                          connect_prob=connect_prob)
            elif algorithm == "nfj":
                G.gen_nfj()
            else:
                G.parallelism = parallelism
                G.layer_num_min = layer_min
                G.layer_num_max = layer_max
                G.connect_prob = connect_prob
                G.gen_rnd_legacy()

            # save and display
            src_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(src_dir, os.pardir, "data")
            G.save(basefolder=data_dir)
            self.display_dag(G, data_dir)
            self.statusBar.showMessage("DAG generated successfully ({})".format(algorithm))

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Parameter", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", str(e))

    def display_dag(self, dag, basefolder):
        """Display the generated DAG image in the GUI."""
        img_path = os.path.join(basefolder, dag.name + '.png')
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            scaled = pixmap.scaledToWidth(450, Qt.SmoothTransformation)
            self.dag_display.setPixmap(scaled)
        else:
            self.dag_display.setText("DAG generated but image not found.")

    def load_config(self):
        """Open a file dialog to load a config JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)")
        if path:
            self._apply_config_file(path)

    def save_config(self):
        """Save current parameters to a JSON config file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "config.json", "JSON Files (*.json)")
        if path:
            try:
                config = {
                    "dag_config": {
                        "parallelism": int(self.edit_parallelism.text()),
                        "layer_num_min": int(self.edit_critical_min.text()),
                        "layer_num_max": int(self.edit_critical_max.text()),
                        "connect_prob": float(self.edit_pc.text())
                    }
                }
                with open(path, 'w') as f:
                    json.dump(config, f, indent=2)
                self.statusBar.showMessage("Configuration saved to " + path)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))

    def load_default_config(self):
        """Load the default config.json from the project root."""
        src_dir = os.path.dirname(os.path.abspath(__file__))
        default_config = os.path.join(src_dir, os.pardir, "config.json")
        if os.path.exists(default_config):
            self._apply_config_file(default_config)
        else:
            QMessageBox.warning(self, "Not Found", "Default config.json not found.")

    def _apply_config_file(self, path):
        """Parse a config file and populate the UI fields."""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            dag_cfg = config.get("dag_config", {})
            self.edit_parallelism.setText(str(dag_cfg.get("parallelism", 4)))
            self.edit_critical_min.setText(str(dag_cfg.get("layer_num_min", 3)))
            self.edit_critical_max.setText(str(dag_cfg.get("layer_num_max", 8)))
            self.edit_pc.setText(str(dag_cfg.get("connect_prob", 0.5)))
            self.statusBar.showMessage("Configuration loaded from " + path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))


# Main function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = daggen_gui()
    sys.exit(app.exec_())
