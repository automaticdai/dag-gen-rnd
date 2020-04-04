# Hosein Kangavar Nazari - CS student, IASBS university
# RealTime course first assinment's Code
# UUnifast for making different task sets

import random
import math

def uunifast(n, U):
    sumU = U
    vectU = []

    for i in range(1, n):
        nextSumU = sumU * random.uniform(0, 1) ** (1.0 / (n-i))
        vectU.append(sumU - nextSumU)
        sumU = nextSumU

    vectU.append(sumU)

    #summation over all utilization for finding global utilization
    AllSum = 0

    for i in range(len(vectU)):
        AllSum += vectU[i]

    return AllSum, vectU


if __name__ == "__main__":
    JOB_NUMBERS = 10 #task number in each list
    UTILIZATION = 1.0 #Utilization
    AllSum, vectU = uunifast(JOB_NUMBERS, UTILIZATION)
    print(AllSum)
    print(vectU)
