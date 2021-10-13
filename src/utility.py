#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################################################################
# Randomized DAG Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
################################################################################

import networkx as nx

def load_task(task_idx, dag_base_folder = "../data/"):
    # << load DAG task <<
    dag_task_file = dag_base_folder + "Tau_{:d}.gpickle".format(task_idx)

    # task is saved as NetworkX gpickle format
    G = nx.read_gpickle(dag_task_file)

    # formulate the graph list
    G_dict = {}
    C_dict = {}
    V_array = []
    max_key = 0
    for u, v, weight in G.edges(data='label'):
        if u not in G_dict:
            G_dict[u] = [v]
        else:
            G_dict[u].append(v)

        if v > max_key:
            max_key = v

        if u not in V_array:
            V_array.append(u)
        if v not in V_array:
            V_array.append(v)

        C_dict[u] = weight
    C_dict[max_key] = 1

    G_dict[max_key] = []

    # formulate the c list (c[0] is c for v1!!)
    C_array = []
    for key in sorted(C_dict):
        C_array.append(C_dict[key])

    V_array.sort()
    W = sum(C_array)

    # >> end of load DAG task >>
    return G_dict, V_array, C_dict, C_array, W


# below is an example of how to use the load function:
if __name__ == "__main__":
    G, V, C, _, W = load_task(task_idx = 1, dag_base_folder = "../data-multi-m4-u2.0/0/")
    print("G: ", G)
    print("V: ", V)
    print("C: ", C)
    print("W: ", W)