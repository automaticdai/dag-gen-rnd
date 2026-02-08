import pytest
import random
import networkx as nx

from rnddag import DAG, DAGTaskset


# ---- DAG.__init__ ----

class TestDAGInit:
    def test_default_init(self):
        d = DAG()
        assert d.name == "Tau_0"
        assert d.U == -1
        assert d.T == -1
        assert d.W == -1
        assert d.L == -1

    def test_parameterized_init(self):
        d = DAG(i=5, U=0.3, T=1000, W=300)
        assert d.name == "Tau_5"
        assert d.U == 0.3
        assert d.T == 1000
        assert d.W == 300

    def test_legacy_defaults_exist(self):
        """gen_rnd_legacy() needs these attributes on the instance."""
        d = DAG()
        assert hasattr(d, 'parallelism')
        assert hasattr(d, 'layer_num_min')
        assert hasattr(d, 'layer_num_max')
        assert hasattr(d, 'connect_prob')


# ---- gen_rnd ----

class TestGenRnd:
    def setup_method(self):
        random.seed(42)
        self.dag = DAG()
        self.dag.gen_rnd(parallelism=4, layer_num_min=3, layer_num_max=6, connect_prob=0.5)
        self.G = self.dag.get_graph()

    def test_produces_dag(self):
        assert isinstance(self.G, nx.DiGraph)
        assert nx.is_directed_acyclic_graph(self.G)

    def test_has_single_source(self):
        sources = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]
        assert len(sources) == 1

    def test_has_single_sink(self):
        sinks = [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
        assert len(sinks) == 1

    def test_is_weakly_connected(self):
        assert nx.is_weakly_connected(self.G)

    def test_node_count_within_bounds(self):
        # minimum: layer_num_min layers with 1 node each (source counted as layer)
        # maximum: roughly (layer_num_max - 2) * parallelism + 2 (source + sink)
        n = self.G.number_of_nodes()
        assert n >= 3  # at least source + 1 internal + sink
        assert n <= (6 - 2) * 4 + 2  # upper bound

    def test_deterministic_with_seed(self):
        random.seed(42)
        d1 = DAG()
        d1.gen_rnd(parallelism=4, layer_num_min=3, layer_num_max=6, connect_prob=0.5)

        random.seed(42)
        d2 = DAG()
        d2.gen_rnd(parallelism=4, layer_num_min=3, layer_num_max=6, connect_prob=0.5)

        assert list(d1.get_graph().nodes()) == list(d2.get_graph().nodes())
        assert list(d1.get_graph().edges()) == list(d2.get_graph().edges())

    def test_graph_attributes(self):
        assert self.G.graph['Index'] == 0
        assert self.G.graph['U'] == -1


# ---- gen_nfj ----

class TestGenNfj:
    def setup_method(self):
        random.seed(42)
        self.dag = DAG()
        self.dag.gen_nfj()
        self.G = self.dag.get_graph()

    def test_produces_dag(self):
        assert isinstance(self.G, nx.DiGraph)
        assert nx.is_directed_acyclic_graph(self.G)

    def test_has_single_source(self):
        sources = [n for n in self.G.nodes() if self.G.in_degree(n) == 0]
        assert len(sources) == 1
        assert sources[0] == 1  # node 1 is always source

    def test_is_weakly_connected(self):
        assert nx.is_weakly_connected(self.G)

    def test_multiple_nodes(self):
        assert self.G.number_of_nodes() >= 2


# ---- gen() dispatcher ----

class TestGenDispatch:
    def test_dispatch_rnd(self):
        random.seed(42)
        d = DAG()
        d.gen("rnd")
        assert nx.is_directed_acyclic_graph(d.get_graph())

    def test_dispatch_nfj(self):
        random.seed(42)
        d = DAG()
        d.gen("nfj")
        assert nx.is_directed_acyclic_graph(d.get_graph())

    def test_dispatch_legacy(self):
        random.seed(42)
        d = DAG()
        d.gen("legacy")
        assert nx.is_directed_acyclic_graph(d.get_graph())


# ---- save() ----

class TestSave:
    @pytest.fixture(autouse=True)
    def _skip_if_no_pygraphviz(self):
        pytest.importorskip("pygraphviz")

    def test_save_creates_files(self, tmp_path):
        random.seed(42)
        d = DAG(i=0)
        d.gen_rnd()
        d.save(basefolder=str(tmp_path))

        assert (tmp_path / "Tau_0.png").exists()
        assert (tmp_path / "Tau_0.gpickle").exists()
        assert (tmp_path / "Tau_0.gml").exists()

    def test_save_creates_directory(self, tmp_path):
        subdir = tmp_path / "output" / "nested"
        random.seed(42)
        d = DAG(i=1)
        d.gen_rnd()
        d.save(basefolder=str(subdir))

        assert subdir.exists()
        assert (subdir / "Tau_1.png").exists()

    def test_gml_roundtrip(self, tmp_path):
        random.seed(42)
        d = DAG(i=0, U=0.5, T=1000, W=500)
        d.gen_rnd(parallelism=3, layer_num_min=3, layer_num_max=5, connect_prob=0.5)
        d.save(basefolder=str(tmp_path))

        G_loaded = nx.read_gml(str(tmp_path / "Tau_0.gml"))
        assert G_loaded.number_of_nodes() == d.get_number_of_nodes()
        assert G_loaded.number_of_edges() == d.get_number_of_edges()


# ---- DAGTaskset ----

class TestDAGTaskset:
    def test_init(self):
        ts = DAGTaskset()
        assert ts.util == 0
        assert ts.task_number == 0
        assert ts.tasks == []
