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
    # Initialize directories
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))

    data_path = os.path.join(base_path, "data")
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    logs_path = os.path.join(base_path, "logs")
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # Parse cmd arguments
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

    # start evaluation
    # create taskset
    Gamma = DAGset()

    # task number
    n = 10

    # DAG 
    utilizations = uunifast_discard(n, u=4.0, nsets=1)

    # DAG period
    period_set = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    periods = gen_period(period_set, n)

    # DAG graph
    for i in range(n):
        w = utilizations[0][i] / periods[i]
        print("Task {}: U = {}, T = {}, W = {}>>".format(i,utilizations[0][i],periods[i], w))
        
        G = DAG(i)
        G.gen()
        #G.save('data/{0}.png'.format(i))
        #G.plot()

        # sub-DAG execution times
        c_ = gen_execution_times(n=25, w=10)
        nx.set_node_attributes(G.graph(), c_, 'c')

        #print(G)
