#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import os, sys, logging, getopt, json
import random
from tqdm import tqdm

from dag_factory import generate_dag, generate_multi_dag_taskset


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_json = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        raise EnvironmentError("Unable to open %s" % (config_path)) from e

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

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # load configuration
    config = parse_configuration(config_path)

    logging.info("Configurations: %s", config)

    ############################################################################
    # load generator basic configuration
    ############################################################################
    # load and set random seed
    random.seed(config["global"]["rnd_seed"])

    # single- or multi-dag
    multi_dag = config["global"]["multi-DAG_on"]

    # utilization algorithm
    util_algo = config["global"].get("util_algorithm", "uunifast_discard")

    # DAG config
    dag_config = config["dag_config"]

    ############################################################################
    # I. single DAG generation
    ############################################################################
    if not multi_dag:
        n = config["single-DAG"]["set_number"]
        w = config["single-DAG"]["workload"]
        dummy = config["global"]["dummy_source_and_sink"]

        for i in tqdm(range(n)):
            G, _ = generate_dag(i=i, dag_config=dag_config, workload=w,
                                round_c=True, dummy=dummy)

            if config["global"]["print_DAG"]:
                G.print_data()

            if config["global"]["save_to_file"]:
                G.save(basefolder=data_path, save_png=config["global"].get("save_png", True))

    ############################################################################
    # II. multi-DAG generation
    ############################################################################
    else:
        n_set = config["multi-DAG"]["set_number"]
        u_total = config["multi-DAG"]["utilization"]
        n = config["multi-DAG"]["task_number_per_set"]
        cores = config["global"]["cores"]
        period_set = config["multi-DAG"]["periods"]
        dummy = config["global"]["dummy_source_and_sink"]

        U_p = []
        prev_set_index = -1

        for set_index, i, G, c_dict in tqdm(
                generate_multi_dag_taskset(
                    dag_config=dag_config, n_tasks=n, n_sets=n_set,
                    u_total=u_total, period_set=period_set, cores=cores,
                    util_algo=util_algo, dummy=dummy),
                total=n_set * n):

            if set_index != prev_set_index:
                if prev_set_index >= 0:
                    logging.info("Total U: %s %s", sum(U_p), U_p)
                    logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                    logging.info("")
                logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                U_p = []
                prev_set_index = set_index

            # calculate actual workload and utilization
            w_p = sum(c_dict.values())
            u_p = w_p / G.T
            U_p.append(u_p)

            if config["global"]["print_DAG"]:
                G.print_data()
                logging.info("")

            if config["global"]["save_to_file"]:
                G.save(basefolder=os.path.join(data_path, "data-multi-m{}-u{:.1f}".format(cores, u_total), str(set_index)),
                       save_png=config["global"].get("save_png", True))

        # log final set
        if prev_set_index >= 0:
            logging.info("Total U: %s %s", sum(U_p), U_p)
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
