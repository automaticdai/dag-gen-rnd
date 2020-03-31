#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

from random import seed, randint, random

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# parameters (default)
rnd_seed = randint(1, 1000)
parallelism = 4
layer_num_max = 7  # critical path
layer_num_min = 3  # critical path
connect_prob = 0.5

class rnddag:
    def __init__(self):
        pass


    def gen(self):
        # data structures
        nodes = []          # nodes in all layers (in form of shape decomposition)
        nodes_parent = []   # nodes that can be parents
        nodes_parent_childless = []  # nodes without child
        nodes_orphan = []   # nodes without any parent

        edges = []

        # initial a new graph
        G = nx.DiGraph()

        # add the root node
        n = 1
        G.add_node(n, rank=0)
        nodes.append([n])
        nodes_parent.append(n)
        n = n + 1

        print(nodes)
        print(edges)

        # random and remove the source and the sink node
        layer_num_this = randint(layer_num_min - 2, layer_num_max - 2)

        # generate layer by layer
        for k in range(layer_num_this):
            # randomised nodes in each layer
            m = randint(1, parallelism)

            nodes_t = []
            for j in range(m):
                nodes_t.append(n)
                nodes_orphan.append(n)
                G.add_node(n, rank=k+1)
                n = n + 1

            nodes.append(nodes_t)

            # initially assume all parents are childless
            nodes_parent_childless[:] = nodes_parent_childless[:] + nodes_parent[:]

            # iterates all nodes in the current layout
            for i in nodes[k+1]:
                for ii in nodes_parent:
                    # add connections
                    if random() < connect_prob:
                        G.add_edge(ii, i)
                        if i in nodes_orphan:
                            nodes_orphan.remove(i)
                        if ii in nodes_parent_childless:
                            nodes_parent_childless.remove(ii)
            # add all childs as candidate parents for the next layer
            nodes_parent[:] = nodes[k+1]

            # connect all orphan to the root node
            for i in nodes_orphan:
                nodes_orphan.remove(i)
                G.add_edge(1, i)
                # if i in nodes_parent:
                #     nodes_parent.remove(i)

        # Dealing with the final layer
        # connect everything together to a final node
        for i in nodes_parent:
            G.add_edge(i, n)

        for i in nodes_parent_childless:
            G.add_edge(i, n)

        # connect all orphan to the root node
        for i in nodes_orphan:
            nodes_orphan.remove(i)
            G.add_edge(1, i)

        # mutate a node to be conditional
        # G.add_node('2', style='filled', fillcolor='red', shape='diamond')

        # handling critical Path


        # set graph properties

        print(nodes)
        #print(nodes_orphan)

        # return the graph
        self.G = G


    def config(self):
        pass


    def plot(self):
        # layout graph
        #A = to_agraph(G)
        A = nx.nx_agraph.to_agraph(self.G)
        print(A)
        print(type(A))
        A.layout('dot')

        # plot graph
        filename = 'output/graph.png'
        A.draw(filename, format="png")

        img = mpimg.imread(filename)
        ypixels, xpixels, bands = img.shape
        dpi = 100.
        xinch = xpixels / dpi
        yinch = ypixels / dpi

        # plot and save in the same size as the original
        plt.figure(figsize=(xinch, yinch))
        ax = plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
        ax.imshow(img, interpolation='none')

        # plt.show(block=False)
        plt.show()


    def save(self):
        pass
