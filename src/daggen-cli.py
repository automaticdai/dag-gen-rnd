#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import os, sys, logging, getopt, time, json
import networkx as nx
import random
from tqdm import tqdm

from rnddag import DAG, DAGTaskset
from generator import uunifast_discard, drs_gen
from generator import gen_period, gen_execution_times


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_json = json.load(config_file)
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return config_json


def print_usage_info():
    logging.info("[Usage] python3 daggen-cli.py --config config_file")


def main(config_path=None, data_path=None):
    """Main entry point for DAG generation.

    Args:
        config_path: Path to config JSON file. Defaults to config.json in project root.
        data_path: Path to output data directory. Defaults to data/ in project root.
    """
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))

    if config_path is None:
        config_path = os.path.join(base_path, "config.json")
    if data_path is None:
        data_path = os.path.join(base_path, "data")

    os.makedirs(data_path, exist_ok=True)

    logs_path = os.path.join(base_path, "logs")
    os.makedirs(logs_path, exist_ok=True)

    # load configuration
    config = parse_configuration(config_path)

    logging.info("Configurations:", config)

    ############################################################################
    # load generator basic configuration
    ############################################################################
    # load and set random seed
    random.seed(config["misc"]["rnd_seed"])

    # single- or multi-dag
    multi_dag = config["misc"]["multi-DAG"]

    # utilization algorithm
    util_algo = config["misc"].get("util_algorithm", "uunifast_discard")

    # DAG config
    dag_config = config["dag_config"]

    ############################################################################
    # I. single DAG generation
    ############################################################################
    if not multi_dag:
        n = config["single_task"]["set_number"]
        w = config["single_task"]["workload"]

        for i in tqdm(range(n)):
            # create a new DAG
            G = DAG(i=i, U=-1, T=-1, W=w)
            G.gen_rnd(parallelism=dag_config["parallelism"],
                      layer_num_min=dag_config["layer_num_min"],
                      layer_num_max=dag_config["layer_num_max"],
                      connect_prob=dag_config["connect_prob"])

            # generate sub-DAG execution times
            n_nodes = G.get_number_of_nodes()
            dummy = config["misc"]["dummy_source_and_sink"]
            c_ = gen_execution_times(n_nodes, w, round_c=True, dummy=dummy)
            nx.set_node_attributes(G.get_graph(), c_, 'C')

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
                G.save(basefolder=data_path)

    ############################################################################
    # II. multi-DAG generation
    ############################################################################
    else:
        # set of tasksets
        n_set = config["multi_task"]["set_number"]

        # total utilization
        u_total = config["multi_task"]["utilization"]

        # task number
        n = config["multi_task"]["task_number_per_set"]

        # number of cores
        cores = config["misc"]["cores"]

        # Load DAG period set (in us)
        period_set = config["multi_task"]["periods"]
        period_set = [(x) for x in period_set]

        # DAG generation main loop
        for set_index in tqdm(range(n_set)):
            logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # create a new taskset
            Gamma = DAGTaskset()

            U_p = []

            # DAG taskset utilization
            if util_algo == "drs":
                U = drs_gen(n, u=u_total, nsets=n_set, ulimit=cores)
            else:
                U = uunifast_discard(n, u=u_total, nsets=n_set, ulimit=cores)

            # generate periods
            periods = gen_period(period_set, n)
            logging.info(periods)

            for i in range(n):
                # calculate workload (in us)
                w = U[set_index][i] * periods[i]

                # create a new DAG
                G = DAG(i=i, U=U[set_index][i], T=periods[i], W=w)

                # generate nodes in the DAG
                # G.gen_nfj()
                G.gen_rnd(parallelism=dag_config["parallelism"],
                          layer_num_min=dag_config["layer_num_min"],
                          layer_num_max=dag_config["layer_num_max"],
                          connect_prob=dag_config["connect_prob"])

                # generate sub-DAG execution times
                n_nodes = G.get_number_of_nodes()
                dummy = config["misc"]["dummy_source_and_sink"]
                c_ = gen_execution_times(n_nodes, w, round_c=True, dummy=dummy)
                nx.set_node_attributes(G.get_graph(), c_, 'C')

                # calculate actual workload and utilization
                w_p = 0
                for item in c_.items():
                    w_p = w_p + item[1]

                u_p = w_p / periods[i]
                U_p.append(u_p)

                # set execution times on edges
                w_e = {}
                for e in G.get_graph().edges():
                    ccc = c_[e[0]]
                    w_e[e] = ccc

                nx.set_edge_attributes(G.get_graph(), w_e, 'label')

                # print internal data
                if config["misc"]["print_DAG"]:
                    G.print_data()
                    logging.info("")

                # save the graph
                if config["misc"]["save_to_file"]:
                    G.save(basefolder=os.path.join(data_path, "data-multi-m{}-u{:.1f}".format(cores, u_total), str(set_index)))

                # (optional) plot the graph
                # G.plot()

            logging.info("Total U:", sum(U_p), U_p)
            logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            logging.info("")


if __name__ == "__main__":
    ############################################################################
    # Parse cmd arguments
    ############################################################################
    src_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.abspath(os.path.join(src_path, os.pardir))

    config_path = os.path.join(base_path, "config.json")

    try:
        short_flags = "hc:d:e"
        long_flags = ["help", "config=", "directory=", "evaluate"]
        opts, args = getopt.getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError as err:
        logging.error(err)
        print_usage_info()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage_info()
            sys.exit()
        elif opt in ("-c", "--config"):
            config_path = arg

    main(config_path=config_path)
