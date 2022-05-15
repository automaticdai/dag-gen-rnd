#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import networkx as nx

G = nx.DiGraph()

# add nodes
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_node(5)

# add edges
G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(3, 4)
G.add_edge(4, 5)
G.add_edge(1, 3)
G.add_edge(3, 5)
G.add_edge(4, 5)

# print
print("Nodes:", G.nodes())
print("Edges:", G.edges())
print("Number of Nodes:", G.number_of_nodes())
print("Number of Edges:", G.number_of_edges())
print("In degree:", G.in_degree)
print("Out degree:",G.out_degree)

# set attributes
nx.set_node_attributes(G, {1:5, 2:6, 4:3}, 'c')
print( nx.get_node_attributes(G, 'c') )

# note: NX DiGraph is iteratble
for j in G:
    pass
