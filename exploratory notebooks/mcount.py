'''           Functions for counting subgraphs of 3 and 4 nodes           '''

#This script contains all functions that count ocurrences of specific
# subgraphs given a particular undirected simple graph. Most of the counting
# formulas were adapted from publications by Duval, Estrada, and Knight.

#RMK: For these to yield the correct result, all graphs must be undirected, 
#      without self-loops, and without parallel edges.

#############################################################################

import numpy as np
import networkx as nx
from itertools import combinations

#############################################################################
'''General subgraph counting'''

#These functions take as input a graph and an 1x8 vector whose entries are
# the counts of the respective subgraphs. The indexation is presented on the
# paper. Notice that they must be called in order, as some might depend upon
# the output of others.

def count_path3(graph, motifs=None):
    s = 0
    for node in graph:
        degree = graph.degree(node)
        s += degree*(degree - 1)
    count = s/2 #because a 3-path will be counted once for each edge
    return count

def count_complete3(graph, motifs=None):
    triangles_dict = nx.triangles(graph)
    t = sum(triangles_dict.values())
    count = t/3 #because a triangle will be counted once for each vertex
    return count

def count_path4(graph, motifs):
    s = 0
    for node_i in graph:
        for node_j in graph.neighbors(node_i):
            if node_j > node_i:
                degree_i = graph.degree(node_i)
                degree_j = graph.degree(node_j)
                s += (degree_i - 1)*(degree_j - 1)
    count = s - 3*motifs[1] #because some of the paths we found will wrap
                            # around, forming a triangle
    return count

def count_star4(graph, motifs=None):
    s = 0
    for node in graph:
        degree = graph.degree(node)
        s += degree*(degree - 1)*(degree - 2)
    count = s/6
    return count

def count_complete4(graph, motifs=None):
    #RMK: Counting cliques is essentially an NP-complete problem. This
    #      function simplifies it significantly, but it will still be
    #      computationally hard.
    s = 0
    for node in graph:
        nb = graph[node]
        sub = graph.subgraph(nb)
        Asub = nx.to_numpy_matrix(sub)
        Asub_cube = np.linalg.matrix_power(Asub, 3)
        s += np.trace(Asub_cube)
    count = s/24
    return count

def count_cycle4(graph, motifs=None):
    s = 0
    for node in graph:
        #we will iterate over all pairs of neighbors of this node and check
        # which ones share another common neighbor---this defines a square.
        for u,w in combinations(graph[node], 2):
            squares = len((set(graph[u]) & set(graph[w])) - set([node]))
            s += squares
    count = s/4 #similar to the triangle count    
    return count

def count_diamond4(graph, motifs=None):
    s = 0
    for node_i in graph:
        for node_j in graph[node_i]:
            #For neighbors, we can find the number of walks of length 2. Note
            # that these are simple graphs, so a walk of length 2 is
            # necessairly a simple 3-path.          
            walks = nx.all_simple_paths(graph, node_i, node_j, 2)
            walk_count = len(list(walks))-1 #This is A^2_{ij}.
            s += walk_count*(walk_count - 1)
            #Note that, since this is a simple graph, the fact that j is in
            # the neighborhood of i necessairly gives that A_{ij} = 1, so we
            # don't need to include this in our calculations.
    count = s/4
    return count

def count_tadpole4(graph, motifs=None):    
    s = 0
    #We count tadpoles by their degree-3 nodes.
    for node in graph:
        degree = graph.degree(node)
        #If the degree is less than 3, the node should not be considered.
        if degree > 2:
            #The number of "tails" is 2 less than the degree of the node, 
            # since two edges are used to make a triangle. If there are no
            # triangles incident to that node, then the term is zero.
            s += nx.triangles(graph, node)*(degree-2)
    count = s  #since each tadpole has 1 degree-3 node, the count is precise
    return count

#The following function produces the motif vector for a graph:
    
def get_motifvector(graph):
    motifs = np.zeros(8)

    motifs[0] = count_path3(graph, motifs)
    motifs[1] = count_complete3(graph, motifs)
    motifs[2] = count_path4(graph, motifs)    
    motifs[3] = count_complete4(graph, motifs)
    motifs[4] = count_star4(graph, motifs)
    motifs[5] = count_cycle4(graph, motifs)
    motifs[6] = count_diamond4(graph, motifs)
    motifs[7] = count_tadpole4(graph, motifs)
    
    return motifs

#############################################################################
'''Non-nested subgraph counting'''

#These functions take as input the subgraph vector produced above and return
# the counts of the respective subgraphs that are not part of other subgraphs
# with the same number of nodes but more edges. That means, complete subgraphs
# are never nested!

def nnest_path3(motifs):
    return motifs[0] - 3*motifs[1]

def nnest_path4(motifs):
    return motifs[2] - 2*motifs[7] - 4*motifs[5] + 6*motifs[6] - 12*motifs[3]

def nnest_star4(motifs):
    return motifs[4] - motifs[7] + 2*motifs[6] - 4*motifs[3]

def nnest_cycle4(motifs):
    return motifs[5] - motifs[6] + 3*motifs[3]

def nnest_diamond4(motifs):
    return motifs[6] - 6*motifs[3]

def nnest_tadpole4(motifs):
    return motifs[7] - 4*motifs[6] + 12*motifs[3]

#The following function produces the non-nested motif vector:

def get_nnest_motifvector(motifs):
    nnest_motifs = np.zeros(8)
    nnest_motifs[0] = nnest_path3(motifs)
    nnest_motifs[1] = motifs[1]
    nnest_motifs[2] = nnest_path4(motifs)
    nnest_motifs[3] = motifs[3]
    nnest_motifs[4] = nnest_star4(motifs)
    nnest_motifs[5] = nnest_cycle4(motifs)
    nnest_motifs[6] = nnest_diamond4(motifs)
    nnest_motifs[7] = nnest_tadpole4(motifs)
    return nnest_motifs

#############################################################################
'''Subgraph counting on random graphs'''

#These functions take as input the number of nodes n and a probability p to
# compute the expected count of each motif in an Erdos-Reniy random graph with
# these parameters. The probability p can be approximated by the number of
# edges of a graph, which is usually the parameter we have.

def random_path3(n,p):
    expectation = n*(n-1)*(n-2)*(p**2)/2
    return expectation

def random_complete3(n,p):
    expectation = n*(n-1)*(n-2)*(p**3)/6
    return expectation

def random_path4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**3)/2
    return expectation

def random_complete4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**6)/24
    return expectation

def random_star4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**3)/6
    return expectation

def random_cycle4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**4)/8
    return expectation

def random_diamond4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**5)/4
    return expectation

def random_tadpole4(n,p):
    expectation = n*(n-1)*(n-2)*(n-3)*(p**4)/2
    return expectation

#To produce the motif vector for a random graph, we take the number of nodes
# and edges as input and compute the link probability ourselves.

def get_random_motifvector(n, m):
    p = 2*m/(n*(n-1))
    
    random_motifs = np.zeros(8)
    
    random_motifs[0] = random_path3(n, p)
    random_motifs[1] = random_complete3(n, p)
    random_motifs[2] = random_path4(n, p)
    random_motifs[3] = random_complete4(n, p)
    random_motifs[4] = random_star4(n, p)
    random_motifs[5] = random_cycle4(n, p)
    random_motifs[6] = random_diamond4(n, p)
    random_motifs[7] = random_tadpole4(n, p)
    
    return random_motifs

def get_randomnnest_motifvector(random_motifs, n, m):
    p = 2*m/(n*(n-1))
    
    exp = np.array([1, 0, 3, 0, 3, 2, 1, 2]) #These were found based on the
                                             # number of edges and vertices
                                             # in the respective motif.    
    multiplier = np.power(np.repeat([1-p], 8), exp)
    randomnest_motifvector = np.multiply(random_motifs, multiplier)
    
    return randomnest_motifvector

#############################################################################