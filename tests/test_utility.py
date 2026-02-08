import pytest
import os
import random
import networkx as nx


requires_pygraphviz = pytest.mark.skipif(
    not pytest.importorskip("pygraphviz", reason="pygraphviz not installed"),
    reason="pygraphviz not installed"
)


@pytest.fixture
def saved_dag(tmp_path):
    """Generate and save a DAG to a temp directory, return (path, DAG)."""
    pytest.importorskip("pygraphviz")
    from rnddag import DAG
    from generator import gen_execution_times

    random.seed(42)
    d = DAG(i=0, U=0.5, T=1000, W=500)
    d.gen_rnd(parallelism=3, layer_num_min=3, layer_num_max=5, connect_prob=0.5)

    n_nodes = d.get_number_of_nodes()
    c_ = gen_execution_times(n_nodes, 500, round_c=True)
    nx.set_node_attributes(d.get_graph(), c_, 'C')

    w_e = {}
    for e in d.get_graph().edges():
        w_e[e] = c_[e[0]]
    nx.set_edge_attributes(d.get_graph(), w_e, 'label')

    d.save(basefolder=str(tmp_path))
    return str(tmp_path), d


class TestLoadTask:
    def test_returns_correct_structure(self, saved_dag):
        from utility import load_task
        folder, _ = saved_dag
        result = load_task(task_idx=0, dag_base_folder=folder)
        assert len(result) == 6
        G_dict, V_array, C_dict, C_array, T, W = result

    def test_graph_dict_keys_are_nodes(self, saved_dag):
        from utility import load_task
        folder, dag = saved_dag
        G_dict, V_array, C_dict, C_array, T, W = load_task(task_idx=0, dag_base_folder=folder)
        # All keys should be valid node IDs
        all_nodes = set(V_array)
        for k in G_dict.keys():
            assert k in all_nodes

    def test_c_dict_values_positive(self, saved_dag):
        from utility import load_task
        folder, _ = saved_dag
        _, _, C_dict, _, _, _ = load_task(task_idx=0, dag_base_folder=folder)
        for v in C_dict.values():
            assert v > 0

    def test_v_array_sorted(self, saved_dag):
        from utility import load_task
        folder, _ = saved_dag
        _, V_array, _, _, _, _ = load_task(task_idx=0, dag_base_folder=folder)
        assert V_array == sorted(V_array)

    def test_nonexistent_file_raises(self, tmp_path):
        from utility import load_task
        with pytest.raises(Exception):
            load_task(task_idx=999, dag_base_folder=str(tmp_path))
