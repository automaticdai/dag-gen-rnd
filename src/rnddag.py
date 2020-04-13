#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# by Xiaotian Dai
# University of York, UK
# 2020

import json
import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

from random import seed, randint, random

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# Class: DAG Taskset
class DAGset:
    def __init__(self):
        self.rnd_seed = randint(1, 1000)
        self.util = 0
        self.task_number = 0
        self.tasks = []


    def gen(self, u, n):
        # generate tasks
        for i in range(self.task_number):
            G = DAG(i)

        # generate utilizations


        # generate periods
        period_sets = [1,2,5,10,20,50,100,200,500,1000]
        random.choice()
        pass

        # generate execution times

        pass


    def dump(self):
        # dump tasksets into a json file
        pass


    def load(self):
        # load tasksets from a json file
        pass


# Class: DAG Task
class DAG:
    def __init__(self, i):
        # parameters (default)
        self.name = 'Tau_{:d}'.format(i)
        self.parallelism = 4
        self.layer_num_max = 5  # critical path
        self.layer_num_min = 5  # critical path

        # for gen()
        self.connect_prob = 0.5

        # for gen_NFJ()
        self.p_fork = 0.2
        self.p_join = 0.8

        self.W = -1
        self.L = -1


    def __str__(self):
        A = nx.nx_agraph.to_agraph(self.G)
        return A.__str__()
    

    def get_graph(self):
        return self.G
    

    def get_number_of_nodes(self):
        return self.G.number_of_nodes()


    def get_number_of_edges(self):
        return self.G.number_of_edges()


    def gen(self):
        # data structures
        nodes = []          # nodes in all layers (in form of shape decomposition)
        nodes_parent = []   # nodes that can be parents
        nodes_parent_childless = []  # nodes without child
        nodes_orphan = []   # nodes without any parent

        # initial a new graph
        G = nx.DiGraph()

        # add the root node
        n = 1
        G.add_node(n, rank=0)
        nodes.append([n])
        nodes_parent.append(n)
        n = n + 1

        # random and remove the source and the sink node
        layer_num_this = randint(self.layer_num_min - 2, self.layer_num_max - 2)

        # generate layer by layer
        for k in range(layer_num_this):
            # randomised nodes in each layer
            m = randint(1, self.parallelism)

            nodes_t = []
            for _ in range(m):
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
                    if random() < self.connect_prob:
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

        # (optional) mutate a node to be conditional
        # G.add_node('2', style='filled', fillcolor='red', shape='diamond')

        #print(nodes)
        #print(nodes_orphan)

        # return the graph
        self.G = G


    def gen_NFJ(self):
        """ Generate Nested Fork-Join DAG
        """
        # data structures
        nodes = []        # nodes in all layers (in form of shape decomposition)
        nodes_parent = [] # nodes that can become parent

        ancestor_dict = {}  # dict stores traces of nodes' all ancestors

        # initial a new graph
        G = nx.DiGraph()
        n = 1
        r = 0

        G.add_node(n, rank=r)
        nodes.append([n])
        nodes_parent.append(n)
        n = n + 1
        r = r + 1

        ancestor_dict[1] = [] 

        # I. fork phase
        for i in range(5):
            nodes_parent_next = []
            for node_p in nodes_parent:
                if random() < self.p_fork or node_p == 1:
                    kk = randint(2, 3)
                    for i in range(kk):
                        G.add_node(n, rank=r)
                        G.add_edge(node_p, n)
                        nodes_parent_next.append(n)
                        ancestor_dict[n] = ancestor_dict[node_p] + [node_p]

                        n = n + 1
                else:
                    nodes_parent_next.append(node_p)
            r = r + 1
            nodes_parent = nodes_parent_next

        print(ancestor_dict)

        # II. join phase
        # table contains all ancestors and nodes list, with ancestor as the key
        # it is a reverse of ancestor_dict
        table = {}
        for i in nodes_parent:
            for j in ancestor_dict[i]:
                ret = table.get(j, None)
                if ret == None:
                    table[j] = [i]
                else:
                    table[j] = table[j] + [i]

        print(table)

        # start to join
        join_list = []
        for node_p in nodes_parent:
            if random() < self.p_join:
                join_list.append(node_p)

        print(join_list)

        # connect edges if all ancestor constraints are satisfied.
        for i in sorted(table.keys()):
            v = table[i]
            print(v)
            if set(v).issubset(set(join_list)):
                G.add_node(n)
                nodes_parent.append(n)

                for cc in v:
                    G.add_edge(cc, n)
                    # remove from join list & parent list
                    join_list.remove(cc)
                    nodes_parent.remove(cc)

                n = n + 1
        
        # connect all terminal nodes to the sink
        if len(nodes_parent) > 1:
            G.add_node(n, rank=r)
            for i in nodes_parent:
                G.add_edge(i, n)

        # return the generated graph
        self.G = G


    def config(self):
        pass


    def save(self, folder="./"):
        # layout graph
        #A = to_agraph(G)
        A = nx.nx_agraph.to_agraph(self.G)
        A.layout('dot')
        # save graph
        A.draw(folder + self.name + '.png', format="png")


    def plot(self, folder="./"):
        img = mpimg.imread(folder + self.name + '.png')
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
