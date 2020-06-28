#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK

import os, sys, logging, getopt, time, json
import networkx as nx
import random
from tqdm import tqdm

from rnddag import DAG, DAGTaskset
from generator import uunifast_discard, uunifast
from generator import gen_period, gen_execution_times_with_dummy


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_json = json.load(config_file)
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return config_json


def print_usage_info():
    print("[Usage] python3 daggen.py --config config_file")


def gen():
    ############################################################################
    # Initialize directories
    ############################################################################
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))

    data_path = os.path.join(base_path, "data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    logs_path = os.path.join(base_path, "logs")
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    ############################################################################
    # Parse cmd arguments
    ############################################################################
    config_path = os.path.join(base_path, "config.json")
    directory = None
    load_jobs = False
    evaluate = False
    train = False

    try:
        short_flags = "hc:d:e"
        long_flags = ["help", "config=", "directory=", "evaluate"]
        opts, args = getopt.getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError as err:
        print(err)
        print_usage_info()
        sys.exit(2)

    print("Options:", opts)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage_info()
            sys.exit()
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in ("-d", "--directory"):
            directory = arg
            load_jobs = True
        elif opt in ("-e", "--evaluate"):
            evaluate = True
        else:
            raise ValueError("Unknown (opt, arg): (%s, %s)" % (opt, arg))

    # load configuration
    config = parse_configuration(config_path)

    print("Configurations:", config)

    ############################################################################
    # start generation
    ############################################################################
    # set number of cores
    cores = config["hardware"]["cores"]

    # set random seed
    random.seed(config["misc"]["rnd_seed"])

    # create a taskset
    Gamma = DAGTaskset()

    # total utilization
    u_total = config["taskset"]["utilization"]

    # task number
    n = config["taskset"]["task_number"]

    ############################################################################
    # single DAG generation
    ############################################################################
    multi_dag = config["misc"]["multi-DAG"]

    if multi_dag == False:
        n = config["single_task"]["task_number"]
        w = config["single_task"]["workload"]
        
        for i in tqdm(range(n)):
            # create a new DAG
            G = DAG(i=i, U=-1, T=-1, W=w)
            G.gen_rnd(parallelism=5, layer_num_min=5, layer_num_max=12, connect_prob=0.5)

            # generate sub-DAG execution times
            n_nodes = G.get_number_of_nodes()
            c_ = gen_execution_times_with_dummy(n_nodes, w, round_c=True)
            nx.set_node_attributes(G.get_graph(), c_, 'c')

            # set execution times on edges
            w_e = {}
            for e in G.get_graph().edges():
                ccc = c_[e[0]]
                w_e[e] = ccc

            nx.set_edge_attributes(G.get_graph(), w_e, 'label')

            # print internal data
            if config["misc"]["print_DAG"]:
                G.print_data()

            # save graph
            if config["misc"]["save_to_file"]:
                G.save(basefolder="./data/")
        
        return

    ############################################################################
    # Multi-DAG generation
    ############################################################################
    # DAG utilization
    # u_max = p * cores
    U = uunifast_discard(n, u=u_total, nsets=1, ulimit=cores)

    # DAG period (in us)
    period_set = config["taskset"]["periods"]
    period_set = [(x * 1000) for x in period_set]
    periods = gen_period(period_set, n)

    # DAG generation main loop
    U_p = []

    for i in tqdm(range(n)):
        # calculate workload (in us)
        w = U[0][i] * (periods[i])
        
        # create a new DAG
        G = DAG(i=i, U=U[0][i], T=periods[i], W=w)
        
        # generate nodes in the DAG
        #G.gen_NFJ()
        G.gen_rnd()
        
        # generate sub-DAG execution times
        n_nodes = G.get_number_of_nodes()
        c_ = gen_execution_times_with_dummy(n_nodes, w, round_c=True)
        nx.set_node_attributes(G.get_graph(), c_, 'c')
        
        # calculate actual workload and utilization
        w_p = 0
        for item in c_.items():
            w_p = w_p + item[1]
        
        u_p = w_p / periods[i]
        U_p.append(u_p)

        #print("Task {}: U = {}, T = {}, W = {}>>".format(i, U[0][i], periods[i], w))
        #print("w = {}, w' = {}, diff = {}".format(w, w_p, (w_p - w) / w * 100))

        # set execution times on edges
        w_e = {}
        for e in G.get_graph().edges():
            ccc = c_[e[0]]
            w_e[e] = ccc

        nx.set_edge_attributes(G.get_graph(), w_e, 'label')

        # print internal data
        if config["misc"]["print_DAG"]:
            G.print_data()

        # save the graph
        if config["misc"]["save_to_file"]:
            G.save(basefolder="./data/")

        # (optional) plot the graph
        #G.plot()

    print("Total U:", sum(U_p), U_p)


if __name__ == "__main__":
    gen()