#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

import os, sys, logging, getopt, time, json
import networkx as nx
from rnddag import DAG, DAGset
from generator import *


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_json = json.load(config_file)
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return config_json


def print_usage_info():
    print("[Usage] python3 daggen.py --config config_file")


if __name__ == "__main__":
    G = DAG(0)
    G.gen_NFJ()
    G.save()
    print(G)

    sys.exit(0)


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

    config = parse_configuration(config_path)

    ############################################################################
    # start generation
    ############################################################################
    # create taskset
    Gamma = DAGset()

    # total utilization
    u_total = 8.0

    # number of partitions
    p = 2

    # number of cores per partition
    cores = 4

    # task number
    n = 10

    # DAG 
    # u_max = p * cores
    U = uunifast_discard(n, u=u_total, nsets=1, ulimit=cores)

    # DAG period (in us)
    period_set = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    period_set = [(x * 1000) for x in period_set]
    periods = gen_period(period_set, n)

    # DAG graph
    U_p = []
    for i in range(n):
        # calculate workload (in us)
        w = U[0][i] * (periods[i])
        
        G = DAG(i)
        G.gen_NFJ()
        #G.save('data/{}.png'.format(i))
        #G.plot()
        
        n_nodes = G.get_number_of_nodes()
        
        # sub-DAG execution times
        c_ = gen_execution_times(n_nodes, w, round_c=True)
        nx.set_node_attributes(G.get_graph(), c_, 'c')

        # calculate actual workload and utilization
        w_p = 0
        for item in c_.items():
            w_p = w_p + item[1]
        
        u_p = w_p / periods[i]
        U_p.append(u_p)

        print("Task {}: U = {}, T = {}, W = {}>>".format(i, U[0][i],
                                                        periods[i], w))
        print("w = {}, w' = {}, diff = {}".format(w, w_p, (w_p - w) / w * 100))

        print(G)
    
    print("Total U:", sum(U_p), U_p)
