import pytest

import dag_factory
from dag_factory import generate_dag, generate_multi_dag_taskset

DAG_CONFIG = {"parallelism": 4, "layer_num_min": 3, "layer_num_max": 6, "connect_prob": 0.5}


@pytest.fixture
def calls(monkeypatch):
    """Record which DAG generation method generate_dag dispatches to."""
    recorded = []
    for name in ("gen_rnd", "gen_nfj", "gen_rnd_legacy"):
        original = getattr(dag_factory.DAG, name)

        def spy(self, *args, _name=name, _orig=original, **kwargs):
            recorded.append(_name)
            return _orig(self, *args, **kwargs)

        monkeypatch.setattr(dag_factory.DAG, name, spy)
    return recorded


class TestGenerateDagAlgorithm:
    @pytest.mark.parametrize("algorithm, method", [
        ("rnd", "gen_rnd"),
        ("nfj", "gen_nfj"),
        ("legacy", "gen_rnd_legacy"),
    ])
    def test_dispatch(self, calls, algorithm, method):
        G, c_dict = generate_dag(i=0, dag_config=DAG_CONFIG, workload=1000, algorithm=algorithm)
        assert calls == [method]
        assert len(c_dict) == G.get_number_of_nodes()

    def test_default_is_rnd(self, calls):
        generate_dag(i=0, dag_config=DAG_CONFIG, workload=1000)
        assert calls == ["gen_rnd"]

    def test_unknown_algorithm_raises(self):
        with pytest.raises(ValueError, match="bogus"):
            generate_dag(i=0, dag_config=DAG_CONFIG, workload=1000, algorithm="bogus")

    def test_multi_dag_passes_algorithm(self, calls):
        list(generate_multi_dag_taskset(
            dag_config=DAG_CONFIG, n_tasks=2, n_sets=1, u_total=0.5,
            period_set=[1000, 2000, 5000], cores=2, algorithm="nfj"))
        assert calls == ["gen_nfj", "gen_nfj"]
