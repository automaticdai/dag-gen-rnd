#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import os
import networkx as nx

from random import randint, random

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# Class: DAG (Directed Acyclic Graph Task)
class DAG:
    def __init__(self, i=0, U=-1, T=-1, W=-1):
        # parameters (or use default)
        self.task_num = i
        self.name = 'Tau_{:d}'.format(i)
        self.U = U
        self.T = T
        self.W = W

    def __str__(self):
        A = nx.nx_agraph.to_agraph(self.G)
        return A.__str__()

    def get_graph(self):
        return self.G

    def get_number_of_nodes(self):
        return self.G.number_of_nodes()

    def get_number_of_edges(self):
        return self.G.number_of_edges()

    def gen(self, algorithm):
        if algorithm == "nfj":
            self.gen_nfj()
        elif algorithm == "rnd":
            self.gen_rnd()
        else:
            self.gen_rnd_legacy()

    def _generate_layer_by_layer(self, parallelism, layer_num_min, layer_num_max, connect_prob):
        """Shared implementation for layer-by-layer random DAG generation."""
        nodes = []
        nodes_parent = []
        nodes_parent_childless = []
        nodes_orphan = []

        G = nx.DiGraph(Index=self.task_num, U=self.U, T=self.T, W=self.W)

        # add the root node
        n = 1
        G.add_node(n, rank=0)
        nodes.append([n])
        nodes_parent.append(n)
        n = n + 1

        # random and remove the source and the sink node
        layer_num_this = randint(layer_num_min - 2, layer_num_max - 2)

        # generate layer by layer
        for k in range(layer_num_this):
            m = randint(1, parallelism)

            nodes_t = []
            for _ in range(m):
                nodes_t.append(n)
                nodes_orphan.append(n)
                G.add_node(n, rank=k+1)
                n = n + 1

            nodes.append(nodes_t)

            nodes_parent_childless[:] = nodes_parent_childless[:] + nodes_parent[:]

            for i in nodes[k+1]:
                for ii in nodes_parent:
                    if random() < connect_prob:
                        G.add_edge(ii, i)
                        if i in nodes_orphan.copy():
                            nodes_orphan.remove(i)
                        if ii in nodes_parent_childless.copy():
                            nodes_parent_childless.remove(ii)

            nodes_parent[:] = nodes[k+1]

            for i in nodes_orphan.copy():
                G.add_edge(1, i)
                nodes_orphan.remove(i)

        # connect everything together to a final node
        for i in nodes_parent:
            G.add_edge(i, n)

        for i in nodes_parent_childless:
            G.add_edge(i, n)

        for i in nodes_orphan.copy():
            G.add_edge(1, i)
            nodes_orphan.remove(i)

        self.G = G

    def gen_rnd_legacy(self, parallelism=8, layer_num_min=5, layer_num_max=12, connect_prob=0.5):
        self._generate_layer_by_layer(
            parallelism, layer_num_min, layer_num_max, connect_prob)

    def gen_rnd(self, parallelism=8, layer_num_min=5, layer_num_max=12, connect_prob=0.5):
        self._generate_layer_by_layer(
            parallelism, layer_num_min, layer_num_max, connect_prob)

    def gen_nfj(self, depth=5, p_fork=0.3, p_join=0.8, fork_n_min=2, fork_n_max=4):
        """Generate Nested Fork-Join DAG."""
        # data structures
        nodes = []        # nodes in all layers (in form of shape decomposition)
        nodes_parent = [] # nodes that can become parent

        ancestor_dict = {}  # dict stores traces of nodes' all ancestors

        # initial a new graph
        G = nx.DiGraph(Index=self.task_num, U=self.U, T=self.T, W=self.W)
        n = 1
        r = 0

        G.add_node(n, rank=r)
        nodes.append([n])
        nodes_parent.append(n)
        n = n + 1
        r = r + 1

        ancestor_dict[1] = []

        layer_num = max(depth - 2, 0)

        # I. fork phase
        for i in range(layer_num):
            nodes_parent_next = []
            fork_happened = False
            for node_p in nodes_parent:
                if random() < p_fork or node_p == 1:
                    kk = randint(fork_n_min, fork_n_max)
                    for i in range(kk):
                        G.add_node(n, rank=r)
                        G.add_edge(node_p, n, label="n/a")
                        nodes_parent_next.append(n)
                        ancestor_dict[n] = ancestor_dict[node_p] + [node_p]

                        fork_happened = True

                        n = n + 1
                else:
                    nodes_parent_next.append(node_p)
            
            if fork_happened:
                r = r + 1
            
            nodes_parent = nodes_parent_next

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

        # start to join
        join_list = []
        for node_p in nodes_parent:
            if random() < p_join:
                join_list.append(node_p)

        # connect edges if all ancestor constraints are satisfied.
        joined_happened = False
        for i in sorted(table.keys()):
            v = table[i]
            if set(v).issubset(set(join_list)):
                G.add_node(n, rank=r)
                nodes_parent.append(n)

                for cc in v:
                    G.add_edge(cc, n, label="n/a")
                    # remove from join list & parent list
                    join_list.remove(cc)
                    nodes_parent.remove(cc)
                    joined_happened = True
                
                n = n + 1
        
        if joined_happened:
            r = r + 1

        # connect all terminal nodes to the sink
        if len(nodes_parent) > 1:
            G.add_node(n, rank=r)
            for i in nodes_parent:
                G.add_edge(i, n)

        # return the generated graph
        self.G = G

    def print_data(self):
        print(self.G.nodes.data())
        print(self.G.edges.data())

    def save(self, basefolder=None, save_png=True):
        if basefolder is None:
            basefolder = os.path.join(".", "data")

        # create basefolder (if not exists)
        os.makedirs(basefolder, exist_ok=True)

        # save graph (png)
        if save_png:
            A = nx.nx_agraph.to_agraph(self.G)
            A.layout(prog='dot')
            A.draw(os.path.join(basefolder, self.name + '.png'), format="png")

        # save graph (gpickle)
        gpickle_path = os.path.join(basefolder, self.name + '.gpickle')
        try:
            nx.write_gpickle(self.G, gpickle_path)
        except AttributeError:
            import pickle
            with open(gpickle_path, 'wb') as f:
                pickle.dump(self.G, f, pickle.HIGHEST_PROTOCOL)

        # save graph (gml)
        nx.write_gml(self.G, os.path.join(basefolder, self.name + '.gml'))

    def load(self, basefolder=None):
        if basefolder is None:
            basefolder = os.path.join(".", "data")
        pass

    def plot(self, basefolder=None):
        """ The current version of plot draws the generated png file to benefit
        from AGraph (Graphviz) layout functions.
        """
        if basefolder is None:
            basefolder = os.path.join(".", "data")
        img = mpimg.imread(os.path.join(basefolder, self.name + '.png'))
        ypixels, xpixels, bands = img.shape
        dpi = 100.
        xinch = xpixels / dpi
        yinch = ypixels / dpi

        # plot and save in the same size as the original
        plt.figure(figsize=(xinch, yinch))
        ax = plt.axes([0., 0., 1., 1.], frameon=False, xticks=[], yticks=[])
        ax.imshow(img, interpolation='none')

        plt.show()


if __name__ == "__main__":
    G = DAG()
    G.gen("nfj")
    G.save(basefolder=".")
    G.plot(basefolder=".")
