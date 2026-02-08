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
                             QPushButton, QFormLayout, QHBoxLayout, QVBoxLayout,
                             QMessageBox, QFileDialog, QScrollArea, QProgressBar,
                             QComboBox, QLineEdit, QCheckBox, QMenu, QAction)

import networkx as nx

import rnddag
from generator import uunifast_discard, drs_gen, gen_period, gen_execution_times


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

        # progress bar (embedded in status bar, hidden until generation starts)
        self.progressBar = QProgressBar()
        self.progressBar.setFixedWidth(200)
        self.progressBar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progressBar)

        # config UI layout
        self.gui()

        # start the window
        self.setGeometry(300, 300, 900, 600)
        self.setWindowTitle('dag-gen-rnd: Randomised DAG Generator')
        self.show()

    def gui(self):
        # ---- Left panel: parameter form ----
        label = QLabel("<b>Parameter Configurations:</b>")

        self.opt_algorithm = QComboBox()
        self.opt_algorithm.addItem("Default (rnd)")
        self.opt_algorithm.addItem("Random Legacy (rnd_legacy)")
        self.opt_algorithm.addItem("Nested-Fork Join (nfj)")

        self.check_conditional = QCheckBox()
        self.check_mcs_dag = QCheckBox()

        # mode selector
        self.opt_mode = QComboBox()
        self.opt_mode.addItem("Single DAG")
        self.opt_mode.addItem("Multi-DAG")

        # DAG shape parameters (shared by both modes)
        self.edit_parallelism = QLineEdit()
        self.edit_critical_max = QLineEdit()
        self.edit_critical_min = QLineEdit()
        self.edit_pc = QLineEdit()
        self.edit_mcs = QLineEdit()

        # single-DAG specific
        self.edit_workload = QLineEdit()
        self.label_workload = QLabel("Workload:")

        # multi-DAG specific
        self.edit_set_number = QLineEdit()
        self.edit_tasks_per_set = QLineEdit()
        self.edit_utilization = QLineEdit()
        self.edit_periods = QLineEdit()
        self.edit_cores = QLineEdit()
        self.opt_util_algo = QComboBox()
        self.opt_util_algo.addItem("UUniFast-discard")
        self.opt_util_algo.addItem("DRS")

        self.label_set_number = QLabel("Number of sets:")
        self.label_tasks_per_set = QLabel("Tasks per set:")
        self.label_utilization = QLabel("Total utilization:")
        self.label_periods = QLabel("Periods (comma-sep):")
        self.label_cores = QLabel("Cores:")
        self.label_util_algo = QLabel("Utilization algorithm:")

        self.button_gen_conf = QPushButton('Load Default Configuration')
        self.button_gen = QPushButton('Generate DAGs')

        formLayout = QFormLayout()
        formLayout.addRow(label)
        formLayout.addRow("&Mode:", self.opt_mode)
        formLayout.addRow("&Algorithm:", self.opt_algorithm)
        formLayout.addRow("&Maximum parallelism <font color='blue'>>=1</font>:", self.edit_parallelism)
        formLayout.addRow("Min critical path length <font color='blue'>>=3</font>:", self.edit_critical_min)
        formLayout.addRow("Max critical path length <font color='blue'>>=3</font>:", self.edit_critical_max)
        formLayout.addRow("p(Connection) <font color='blue'>[0,1]</font>:", self.edit_pc)
        formLayout.addRow(self.label_workload, self.edit_workload)
        formLayout.addRow(self.label_set_number, self.edit_set_number)
        formLayout.addRow(self.label_tasks_per_set, self.edit_tasks_per_set)
        formLayout.addRow(self.label_utilization, self.edit_utilization)
        formLayout.addRow(self.label_periods, self.edit_periods)
        formLayout.addRow(self.label_cores, self.edit_cores)
        formLayout.addRow(self.label_util_algo, self.opt_util_algo)
        formLayout.addRow("&Mixed-criticality DAG?", self.check_mcs_dag)
        formLayout.addRow("p(High)", self.edit_mcs)
        formLayout.addRow("&Conditional DAG?", self.check_conditional)
        formLayout.addRow(self.button_gen_conf)
        formLayout.addRow(self.button_gen)

        left_widget = QWidget()
        left_widget.setLayout(formLayout)
        left_widget.setFixedWidth(350)

        # ---- Right panel: DAG visualisation ----
        self.dag_display = QLabel("No DAG generated yet.")
        self.dag_display.setAlignment(Qt.AlignCenter)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.dag_display)
        scroll_area.setWidgetResizable(True)

        right_layout = QVBoxLayout()
        right_label = QLabel("<b>DAG Visualisation:</b>")
        right_layout.addWidget(right_label)
        right_layout.addWidget(scroll_area)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # ---- Main horizontal layout ----
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget, 1)

        # set some default values
        self.edit_parallelism.setText("4")
        self.edit_critical_max.setText("7")
        self.edit_critical_min.setText("3")
        self.edit_pc.setText("0.5")
        self.edit_mcs.setText("0.5")
        self.edit_workload.setText("10000")
        self.edit_set_number.setText("10")
        self.edit_tasks_per_set.setText("5")
        self.edit_utilization.setText("0.8")
        self.edit_periods.setText("1000,2000,5000")
        self.edit_cores.setText("4")

        # set initial mode visibility
        self._update_mode_visibility()

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
        self.opt_mode.currentIndexChanged.connect(self._update_mode_visibility)

        # create central widget
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _update_mode_visibility(self):
        """Show/hide widgets based on mode selection."""
        is_multi = self.opt_mode.currentIndex() == 1
        # single-DAG fields
        self.label_workload.setVisible(not is_multi)
        self.edit_workload.setVisible(not is_multi)
        # multi-DAG fields
        for widget in (self.label_set_number, self.edit_set_number,
                       self.label_tasks_per_set, self.edit_tasks_per_set,
                       self.label_utilization, self.edit_utilization,
                       self.label_periods, self.edit_periods,
                       self.label_cores, self.edit_cores,
                       self.label_util_algo, self.opt_util_algo):
            widget.setVisible(is_multi)

    def _read_dag_params(self):
        """Read and validate common DAG shape parameters from the UI."""
        algo_text = self.opt_algorithm.currentText()
        parallelism = int(self.edit_parallelism.text())
        layer_min = int(self.edit_critical_min.text())
        layer_max = int(self.edit_critical_max.text())
        connect_prob = float(self.edit_pc.text())

        if parallelism < 1:
            raise ValueError("Parallelism must be >= 1")
        if layer_min < 3:
            raise ValueError("Min critical path length must be >= 3")
        if layer_max < layer_min:
            raise ValueError("Max must be >= Min critical path length")
        if not (0.0 <= connect_prob <= 1.0):
            raise ValueError("Connection probability must be in [0, 1]")

        if "rnd_legacy" in algo_text:
            algorithm = "legacy"
        elif "nfj" in algo_text:
            algorithm = "nfj"
        else:
            algorithm = "rnd"

        return algorithm, parallelism, layer_min, layer_max, connect_prob

    def _generate_dag_structure(self, G, algorithm, parallelism, layer_min, layer_max, connect_prob):
        """Generate DAG structure using the selected algorithm."""
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

    def event_on_button_gen_clicked(self):
        try:
            algorithm, parallelism, layer_min, layer_max, connect_prob = self._read_dag_params()

            src_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(src_dir, os.pardir, "data")

            self.button_gen.setEnabled(False)
            self.progressBar.setValue(0)
            self.progressBar.setVisible(True)
            QApplication.processEvents()

            if self.opt_mode.currentIndex() == 0:
                # --- Single DAG mode ---
                workload = int(self.edit_workload.text())
                if workload < 1:
                    raise ValueError("Workload must be >= 1")

                self.progressBar.setMaximum(1)
                self.statusBar.showMessage("Generating DAG...")
                QApplication.processEvents()

                G = rnddag.DAG(i=0, W=workload)
                self._generate_dag_structure(G, algorithm, parallelism, layer_min, layer_max, connect_prob)

                n_nodes = G.get_number_of_nodes()
                c_ = gen_execution_times(n_nodes, workload, round_c=True)
                nx.set_node_attributes(G.get_graph(), c_, 'C')
                w_e = {}
                for e in G.get_graph().edges():
                    w_e[e] = c_[e[0]]
                nx.set_edge_attributes(G.get_graph(), w_e, 'label')

                G.save(basefolder=data_dir)
                self.progressBar.setValue(1)
                self.display_dag(G, data_dir)
                self.statusBar.showMessage("DAG generated successfully ({})".format(algorithm))
            else:
                # --- Multi-DAG mode ---
                n_set = int(self.edit_set_number.text())
                n_tasks = int(self.edit_tasks_per_set.text())
                u_total = float(self.edit_utilization.text())
                cores = int(self.edit_cores.text())
                period_set = [int(p.strip()) for p in self.edit_periods.text().split(",")]

                if n_set < 1:
                    raise ValueError("Number of sets must be >= 1")
                if n_tasks < 1:
                    raise ValueError("Tasks per set must be >= 1")
                if u_total <= 0:
                    raise ValueError("Total utilization must be > 0")
                if cores < 1:
                    raise ValueError("Cores must be >= 1")
                if not period_set:
                    raise ValueError("At least one period value is required")

                total_dags = n_set * n_tasks
                self.progressBar.setMaximum(total_dags)
                self.statusBar.showMessage("Generating {} DAGs...".format(total_dags))
                QApplication.processEvents()

                util_algo_text = self.opt_util_algo.currentText()
                if "DRS" in util_algo_text:
                    U = drs_gen(n_tasks, u=u_total, nsets=n_set, ulimit=cores)
                else:
                    U = uunifast_discard(n_tasks, u=u_total, nsets=n_set, ulimit=cores)

                first_dag = None
                first_dag_dir = None
                count = 0

                for set_index in range(n_set):
                    periods = gen_period(period_set, n_tasks)

                    for i in range(n_tasks):
                        w = U[set_index][i] * periods[i]
                        G = rnddag.DAG(i=i, U=U[set_index][i], T=periods[i], W=w)
                        self._generate_dag_structure(G, algorithm, parallelism, layer_min, layer_max, connect_prob)

                        n_nodes = G.get_number_of_nodes()
                        c_ = gen_execution_times(n_nodes, w, round_c=True)
                        nx.set_node_attributes(G.get_graph(), c_, 'C')
                        w_e = {}
                        for e in G.get_graph().edges():
                            w_e[e] = c_[e[0]]
                        nx.set_edge_attributes(G.get_graph(), w_e, 'label')

                        save_dir = os.path.join(data_dir, "data-multi-m{}-u{:.1f}".format(cores, u_total), str(set_index))
                        G.save(basefolder=save_dir)

                        if first_dag is None:
                            first_dag = G
                            first_dag_dir = save_dir

                        count += 1
                        self.progressBar.setValue(count)
                        QApplication.processEvents()

                if first_dag is not None:
                    self.display_dag(first_dag, first_dag_dir)

                self.statusBar.showMessage(
                    "Generated {} tasksets x {} DAGs each ({})".format(n_set, n_tasks, algorithm))

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Parameter", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", str(e))
        finally:
            self.progressBar.setVisible(False)
            self.button_gen.setEnabled(True)

    def display_dag(self, dag, basefolder):
        """Display the generated DAG image in the GUI."""
        img_path = os.path.join(basefolder, dag.name + '.png')
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.dag_display.setPixmap(pixmap)
            self.dag_display.adjustSize()
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
                is_multi = self.opt_mode.currentIndex() == 1
                util_algo = "drs" if "DRS" in self.opt_util_algo.currentText() else "uunifast_discard"
                config = {
                    "misc": {
                        "multi-DAG": is_multi,
                        "cores": int(self.edit_cores.text()),
                        "print_DAG": False,
                        "save_to_file": True,
                        "dummy_source_and_sink": False,
                        "rnd_seed": 1234,
                        "util_algorithm": util_algo
                    },
                    "multi_task": {
                        "set_number": int(self.edit_set_number.text()),
                        "task_number_per_set": int(self.edit_tasks_per_set.text()),
                        "utilization": float(self.edit_utilization.text()),
                        "periods": [int(p.strip()) for p in self.edit_periods.text().split(",")]
                    },
                    "single_task": {
                        "set_number": 1,
                        "workload": int(self.edit_workload.text())
                    },
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

            # dag_config
            dag_cfg = config.get("dag_config", {})
            self.edit_parallelism.setText(str(dag_cfg.get("parallelism", 4)))
            self.edit_critical_min.setText(str(dag_cfg.get("layer_num_min", 3)))
            self.edit_critical_max.setText(str(dag_cfg.get("layer_num_max", 8)))
            self.edit_pc.setText(str(dag_cfg.get("connect_prob", 0.5)))

            # misc
            misc = config.get("misc", {})
            is_multi = misc.get("multi-DAG", False)
            self.opt_mode.setCurrentIndex(1 if is_multi else 0)
            self.edit_cores.setText(str(misc.get("cores", 4)))
            util_algo = misc.get("util_algorithm", "uunifast_discard")
            self.opt_util_algo.setCurrentIndex(1 if util_algo == "drs" else 0)

            # multi_task
            mt = config.get("multi_task", {})
            self.edit_set_number.setText(str(mt.get("set_number", 10)))
            self.edit_tasks_per_set.setText(str(mt.get("task_number_per_set", 5)))
            self.edit_utilization.setText(str(mt.get("utilization", 0.8)))
            periods = mt.get("periods", [1000, 2000, 5000])
            self.edit_periods.setText(",".join(str(p) for p in periods))

            # single_task
            st = config.get("single_task", {})
            self.edit_workload.setText(str(st.get("workload", 10000)))

            self.statusBar.showMessage("Configuration loaded from " + path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))


# Main function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = daggen_gui()
    sys.exit(app.exec_())
