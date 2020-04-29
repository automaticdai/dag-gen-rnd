#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Randomized DAG Generator
# Xiaotian Dai
# Real-Time Systems Group
# University of York, UK

import numpy as np
import random
import math


def uunifast_discard(n, u, nsets, ulimit=1):
    """ UUniFast-discard

    Args:
        n (int): number of tasks
        u (float): total utilization
        nsets (int): number of sets

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

        #print(sum(utilizations))

    return sets


# UUniFast
def uunifast(n, u):
    sumU = u
    vectU = []

    for i in range(1, n):
        nextSumU = sumU * random.uniform(0, 1) ** (1.0 / (n - i))
        vectU.append(sumU - nextSumU)
        sumU = nextSumU

    vectU.append(sumU)

    return vectU


# random generate periods from a population set
def gen_period(population, n):
    periods = []

    for _ in range(n):
        period = random.choice(population)
        periods.append(period)

    return periods


# distribute workloads, w, to n nodes.
def gen_execution_times(n, w, round_c=False):
    c_set = []

    for _ in range(n):
        c = random.random()
        c_set.append(c)

    # sum w'
    w_p = sum(c_set)
    f = w_p / w

    # normalise to w
    c_dict = {}
    for i in range(len(c_set)):
        if round_c == False:
            c_dict[i] = c_set[i] / f
        else:
            # round the value to integer but should be more than 1!
            c_dict[i] = max(round(c_set[i] / f), 1)

    return c_dict


if __name__ == "__main__":
    number_of_tasks = 10

    vectU = uunifast(n=10, u=1.0)
    print(vectU)

    sets = uunifast_discard(n=10, u=4.0, nsets=1)
    print(sets)

    period_set = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    periods = gen_period(period_set, n=10)

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

    c_set = gen_execution_times(n=20, w=100)
    print(c_set)
