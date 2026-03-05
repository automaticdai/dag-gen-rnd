#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Randomized Multi-DAG Task Generator
# Shared DAG generation logic used by both CLI and GUI.
# -------------------------------------------------------------------------------

from rnddag import DAG
from generator import uunifast_discard, drs_gen, gen_period, apply_execution_times


def generate_dag(i, dag_config, workload, algorithm="rnd", utilization=-1,
                 period=-1, round_c=True, dummy=False):
    """Create a single DAG with structure and execution times applied.

    Args:
        i: Task index.
        dag_config: Dict with keys: parallelism, layer_num_min, layer_num_max, connect_prob.
        workload: Total workload to distribute across nodes.
        algorithm: One of "rnd", "nfj", "legacy".
        utilization: Task utilization (-1 if not applicable).
        period: Task period (-1 if not applicable).
        round_c: Whether to round execution times to integers.
        dummy: Whether source/sink nodes get unit execution times.

    Returns:
        Tuple of (DAG, c_dict) where c_dict is the execution time dictionary.
    """
    G = DAG(i=i, U=utilization, T=period, W=workload)

    if algorithm == "rnd":
        G.gen_rnd(parallelism=dag_config["parallelism"],
                  layer_num_min=dag_config["layer_num_min"],
                  layer_num_max=dag_config["layer_num_max"],
                  connect_prob=dag_config["connect_prob"])
    elif algorithm == "nfj":
        G.gen_nfj()
    else:
        G.gen_rnd_legacy(parallelism=dag_config["parallelism"],
                         layer_num_min=dag_config["layer_num_min"],
                         layer_num_max=dag_config["layer_num_max"],
                         connect_prob=dag_config["connect_prob"])

    n_nodes = G.get_number_of_nodes()
    c_dict = apply_execution_times(G, n_nodes, workload, round_c=round_c, dummy=dummy)

    return G, c_dict


def generate_multi_dag_taskset(dag_config, n_tasks, n_sets, u_total, period_set,
                               cores, algorithm="rnd", util_algo="uunifast_discard",
                               dummy=False):
    """Generate a multi-DAG taskset, yielding each DAG as it is created.

    Args:
        dag_config: Dict with DAG shape parameters.
        n_tasks: Number of tasks per set.
        n_sets: Number of tasksets.
        u_total: Total utilization target.
        period_set: List of candidate periods.
        cores: Number of cores (used as utilization upper limit).
        algorithm: DAG generation algorithm.
        util_algo: Utilization generation algorithm ("uunifast_discard" or "drs").
        dummy: Whether source/sink nodes get unit execution times.

    Yields:
        Tuples of (set_index, task_index, DAG, c_dict).
    """
    if util_algo == "drs":
        U = drs_gen(n_tasks, u=u_total, nsets=n_sets, ulimit=cores)
    else:
        U = uunifast_discard(n_tasks, u=u_total, nsets=n_sets, ulimit=cores)

    for set_index in range(n_sets):
        periods = gen_period(period_set, n_tasks)

        for i in range(n_tasks):
            w = U[set_index][i] * periods[i]
            G, c_dict = generate_dag(
                i=i,
                dag_config=dag_config,
                workload=w,
                algorithm=algorithm,
                utilization=U[set_index][i],
                period=periods[i],
                round_c=True,
                dummy=dummy,
            )
            yield set_index, i, G, c_dict
