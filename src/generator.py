# Task Generator

import numpy as np
import random
import math


# UUniFast-discard
def uunifast_discard(n, u, nsets):
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

        # If no task utilization exceeds 1:
        if all(ut <= 1 for ut in utilizations):
            sets.append(utilizations)

        print(sum(utilizations))

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
def gen_period_from_population(population, n):
    periods = []

    for i in range(n):
        period = random.choice(period_set)
        periods.append(period)

    return periods


# distribute workloads, w, to n nodes.
def gen_execution_times(n, w):
    c_set = np.array([])

    for i in range(n):
        c = random.random()
        c_set.append(c)

    c_sum = sum(c_set)
    # normalise to w
    c_set = c_set.div(c_sum)

    return c_set


if __name__ == "__main__":
    vectU = uunifast(10, 1.0)
    print(vectU)

    sets = uunifast_discard(10, 4.0, 100)
    print(sets)

    period_set = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    periods = gen_period_from_population(period_set, 10000)
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


    c_set = gen_execution_times(10, 1)
    print(c_set)
