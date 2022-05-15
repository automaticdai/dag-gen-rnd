#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK
# -------------------------------------------------------------------------------

import numpy as np
import random
import math


# UUniFast
def uunifast(n, u):
    """ Function: UUniFast
    Inputs:
        n (int): number of tasks
        u (float): total utilization
    Returns:
        sets (list)
    """
    sumU = u
    vectU = []

    for i in range(1, n):
        nextSumU = sumU * random.uniform(0, 1) ** (1.0 / (n - i))
        vectU.append(sumU - nextSumU)
        sumU = nextSumU

    vectU.append(sumU)

    return vectU

def uunifast_discard(n, u, nsets, ulimit=1):
    """ Function: UUniFast-discard
    Inputs:
        n (int): number of tasks
        u (float): total utilization
        nsets (int): number of sets
        ulimit: upper limit of the utlization of a single DAG
    Returns:
        sets (list)
    """
    # if (n <= u):
    #     # no feasible solution
    #     return []

    sets = []
    while len(sets) < nsets:
        # Classic UUniFast algorithm:
        utilizations = []
        sumU = u
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        # If no task utilization exceeds ulimit:
        if all(ut <= ulimit for ut in utilizations):
            sets.append(utilizations)

        # print(sum(utilizations))

    return sets

# random generate periods from a population set
def gen_period(population, n):
    periods = []

    for _ in range(n):
        if len(population) == 2:
            # in this case, the period set actually defines a range
            period = random.randint(population[0], population[1])
        else:
            period = random.choice(population)
        periods.append(period)

    return periods


# distribute workloads, w, to n nodes
def gen_execution_times(n, w, round_c=False, dummy=False):
    c_set = []

    if dummy == False:
        for i in range(n):
            c = random.random()
            c_set.append(c)

        # normalise to w & assign to the execution time list
        c_dict = {}
        w_p = sum(c_set)
        f = w_p / w

        for i in range(n):
            if round_c == False:
                # +1 as node number starts from 1, not 0
                c_dict[i + 1] = c_set[i] / f
            else:
                # round the value to integer but should be more than 1!
                c_dict[i + 1] = max(round(c_set[i] / f), 1)

    else:
        # a dummy source / sink node only has unit execution times
        # -> exclude them from the generation process
        # -> append them at the last
        for i in range(n - 2):
            c = random.random()
            c_set.append(c)

        # normalise to w & assign to the execution time list
        w = w - 2 # remove c(source) and c(sink)
        c_dict = {}
        w_p = sum(c_set)
        f = w_p / w

        # dummy source node
        c_dict[1] = 1

        for i in range(n - 2):
            if round_c == False:
                # +1 as node number starts from 1, not 0
                # +1 more as the source node is skipped
                c_dict[i + 1 + 1] = c_set[i] / f
            else:
                # round the value to integer but should be more than 1!
                c_dict[i + 1 + 1] = max(round(c_set[i] / f), 1)

        # dummy sink node
        c_dict[n] = 1

    return c_dict


if __name__ == "__main__":
    number_of_tasks = 10

    print(">> Utilization:")

    vectU = uunifast(n=10, u=1.0)
    print(vectU)

    sets = uunifast_discard(n=10, u=4.0, nsets=1)
    print(sets)

    print(">> Period:")

    period_set = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    periods = gen_period(period_set, n=10000)

    # test the uniformality
    print(periods.count(1),
        periods.count(2),
        periods.count(5),
        periods.count(10),
        periods.count(20),
        periods.count(50),
        periods.count(100),
        periods.count(200),
        periods.count(500),
        periods.count(1000))

    print(">> Execution Times:")
    c_set = gen_execution_times(n=10, w=1000, round_c=True)
    print(c_set)

    c_set = gen_execution_times_with_dummy(n=10, w=1000, round_c=True)
    print(c_set)
