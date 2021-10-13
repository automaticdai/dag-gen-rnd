#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
################################################################################

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
    print("[Usage] python3 daggen-cli.py --config config_file")


if __name__ == "__main__":
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
    # load generator basic configurarion
    ############################################################################
    # set random seed
    random.seed(config["misc"]["rnd_seed"])

    # multi- or single-dag
    multi_dag = config["misc"]["multi-DAG"]

    ############################################################################
    # I. single DAG generation
    ############################################################################
    if multi_dag == False:
        n = config["single_task"]["set_number"]
        w = config["single_task"]["workload"]
        
        for i in tqdm(range(n)):
            # create a new DAG
            G = DAG(i=i, U=-1, T=-1, W=w)
            G.gen_rnd(parallelism=8, layer_num_min=5, layer_num_max=12, connect_prob=0.5)

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
        
        sys.exit(0)

    ############################################################################
    # II. multi-DAG generation
    ############################################################################
    # set of tasksets
    n_set = config["taskset"]["set_number"]

    # total utilization
    u_total = config["taskset"]["utilization"]

    # task number
    n = config["taskset"]["task_number"]

    # number of cores
    cores = config["hardware"]["cores"]

    # create a taskset
    Gamma = DAGTaskset()

    # DAG utilization
    U = uunifast_discard(n, u=u_total, nsets=n_set, ulimit=cores)

    # DAG period (in us)
    period_set = config["taskset"]["periods"]
    period_set = [(x) for x in period_set]
    periods = gen_period(period_set, n)

    # DAG generation main loop
    for set_index in tqdm(range(n_set)):
        U_p = []
        for i in range(n):
            # calculate workload (in us)
            w = U[set_index][i] * periods[i]
            
            # create a new DAG
            G = DAG(i=i, U=U[set_index][i], T=periods[i], W=w)
            
            # generate nodes in the DAG
            #G.gen_NFJ()
            G.gen_rnd(parallelism=3, layer_num_min=3, layer_num_max=5, connect_prob=0.5)
            
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
                G.save(basefolder="./data-multi-m{}-u{:.1f}/{}/".format(cores, u_total, set_index))

            # (optional) plot the graph
            #G.plot()

        print("Total U:", sum(U_p), U_p)
    
    sys.exit(0)
