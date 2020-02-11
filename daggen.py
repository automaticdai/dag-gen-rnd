#!/usr/bin/python3

import networkx as nx
from   networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import json

# read configurations
with open('config.json', 'r') as f:
    array = json.load(f)

print (array["tg"])


# initial a new graph
G = nx.DiGraph()

# add nodes
G.add_node('n_1',rank=0)
G.add_nodes_from(['n_2','n_3','n_4'],style='filled',fillcolor='red',shape='diamond')
G.add_nodes_from(['E','F','G'])
G.add_nodes_from(['H'],label='target')

# add edges
G.add_edge('n_1','n_2',arrowsize=2.0)
G.add_edge('n_1','n_3',penwidth=2.0)
G.add_edge('n_1','n_4')
G.add_edges_from([('B','E'),('B','F')],color='blue')
G.add_edges_from([('C','E'),('C','G')])
G.add_edges_from([('D','F'),('D','G')])
G.add_edges_from([('E','H'),('F','H'),('G','H')])

# set graph properties
G.graph['graph']={'rankdir':'TD'}
G.graph['node']={'shape':'circle'}
G.graph['edges']={'arrowsize':'2.0'}

# layout graph
A = to_agraph(G)
print(A)
A.layout('dot')

# plot graph
filename = 'output/abcd.png'
A.draw(filename)

img = mpimg.imread(filename)
plt.imshow(img)
plt.show()
