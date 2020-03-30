#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

import os, sys, logging, getopt, time, yaml


def parse_configuration(config_path):
    try:
        with open(config_path, "r") as config_file:
            config_yaml = config_file.read()
    except:
        raise EnvironmentError("Unable to open %s" % (config_path))

    return yaml.load(config_yaml)


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

    # Parse arguments
    config_path = None
    directory = None
    load_jobs = False
    evaluate = False
    train = False

    try:
        short_flags = "c:d:e:h"
        long_flags = ["help", "config=", "directory=", "evaluate", "train"]
        opts, args = getopt.getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError as err:
        print(err)
        print_usage_info()
        sys.exit(2)

    print(opts)

    # Print help message
    if len(opts) == 0:
        print_usage_info()
        sys.exit()

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
