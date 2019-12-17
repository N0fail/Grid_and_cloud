import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import networkx as nx

def evaluate(G, nodes, nodes_minus, m, ind_set):
    #G - спиок множеств смежности
    #nodes - множество не удаленных вершин
    #nodes_minus - множество удаленных вершин
    #m - число ребер
    #ind_set - множества независимости в текущем графе

    n = len(nodes)
    beta0 = max(map(lambda x: len(x - nodes_minus), ind_set)) #число независимости

    lower = math.ceil(n/beta0) #оценка с исп. числа независимости
    new_lower = math.ceil(n*n/(n*n - 2*m)) #оценка Геллера
    lower = max(lower, new_lower)

    upper = math.floor(1/2 + math.sqrt(2*m + 1/4)) #верхняя оценка числом рёбер
    new_upper = n - beta0 + 1 #оценка с исп. числа независимости
    upper = min(upper, new_upper)

    return lower, upper


def Bron(G, nodes):
    results = []

    def check(candidates, wrong):
        for i in wrong:
            q = True
            if G[i] & candidates:
                q = False
            if q: return False
        return True

    def extend(compsub, candidates, wrong):

        while candidates and check(candidates, wrong):
            #v = candidates[0]
            v = next(iter(candidates))
            compsub |= set([v])

            new_candidates = candidates - G[v] - set([v])
            #new_candidates = [i for i in candidates if not m[i][v] and i != v]
            new_wrong = wrong - G[v] - set([v])
            #new_wrong = [i for i in wrong if not m[i][v] and i != v]

            if not new_candidates and not new_wrong:
                results.append(compsub.copy())
            else:
                extend(compsub, new_candidates, new_wrong)

            candidates -= set([v])
            compsub -= set([v])
            wrong |= set([v])

    extend(set(), nodes, set())

    return results


def permutation_generator(ones, cur_ones, x, right=-1):
    if ones == cur_ones:
        yield x
    else:
        for i in range(right + 1, len(x)):
            x[i] = 1
            yield from permutation_generator(ones, cur_ones+1, x, i)
            x[i] = 0


def colorize_numpy(G, nodes):
    ind_set = Bron(G, nodes.copy())
    m = sum(map(lambda x: len(x), G)) / 2

    lower, upper = evaluate(G, nodes, set(), m, ind_set)

    G_comp = list()  # дополнение графа
    for i in nodes:
        G_comp.append(nodes.copy() - G[i])
    max_cliques = Bron(G_comp, nodes.copy())  # поиск макс. клики с помощью дополнения

    lower_new = max(map(lambda x: len(x), max_cliques))
    lower = max(lower, lower_new)

    matr = np.zeros((len(nodes), len(ind_set)), dtype=np.byte)
    for idx, ind in enumerate(ind_set):
        matr[list(ind), idx] = 1
    #global counter
    for i in range(lower, upper + 1):
        x = np.zeros((len(ind_set)), dtype=np.byte)
        for comb in permutation_generator(i, 0, x):
            if (matr@comb).prod() != 0:
                return ind_set, comb

if __name__ == "__main__":
    n, m, seed = map(lambda x: int(x), sys.argv[1:-1])
    user = sys.argv[-1]
    G = nx.gnm_random_graph(n, m, seed=seed)
    S = set()
    X = [set()]
    T = set(G.nodes())
    GS = []
    colors = ['g',]*n
    for v in G.nodes:
        GS.append(set(G.adj[v].keys()))
    ind_set, comb = colorize_numpy(GS, T)
    for idx, ind in enumerate(ind_set):
        if comb[idx] == 1:
            for i in ind_set[idx]:
                colors[i] = idx
    nx.draw(G, node_color=colors, pos=nx.drawing.layout.kamada_kawai_layout(G), with_labels=True)
    plt.savefig("{}_{}_{}_{}.png".format(n, m, seed, user))
