import pytest
import random

from generator import uunifast_discard, drs_gen, gen_period, gen_execution_times


# ---- uunifast_discard ----

class TestUunifastDiscard:
    def test_returns_nsets(self):
        sets = uunifast_discard(n=5, u=1.0, nsets=3, ulimit=1)
        assert len(sets) == 3

    def test_respects_ulimit(self):
        sets = uunifast_discard(n=5, u=2.0, nsets=5, ulimit=1)
        for s in sets:
            for v in s:
                assert v <= 1.0

    def test_each_set_sums_to_u(self):
        sets = uunifast_discard(n=5, u=1.5, nsets=3, ulimit=2)
        for s in sets:
            assert sum(s) == pytest.approx(1.5)

    def test_each_set_has_n_elements(self):
        sets = uunifast_discard(n=6, u=1.0, nsets=2, ulimit=1)
        for s in sets:
            assert len(s) == 6

    def test_high_ulimit_no_discard(self):
        """With a very high ulimit, all generated sets should be accepted."""
        random.seed(99)
        sets = uunifast_discard(n=5, u=1.0, nsets=10, ulimit=100)
        assert len(sets) == 10


# ---- gen_period ----

class TestGenPeriod:
    def test_length(self):
        periods = gen_period([100, 200, 500], n=7)
        assert len(periods) == 7

    def test_from_discrete_set(self):
        population = [100, 200, 500, 1000]
        periods = gen_period(population, n=20)
        for p in periods:
            assert p in population

    def test_range_mode(self):
        """When population has exactly 2 elements, it defines a range."""
        periods = gen_period([10, 50], n=100)
        for p in periods:
            assert 10 <= p <= 50

    def test_single_choice_population(self):
        """With 3+ element population, picks from the set."""
        population = [100, 200, 300]
        random.seed(42)
        periods = gen_period(population, n=50)
        for p in periods:
            assert p in population


# ---- gen_execution_times ----

class TestGenExecutionTimes:
    def test_length(self):
        c = gen_execution_times(n=10, w=1000)
        assert len(c) == 10

    def test_keys_one_indexed(self):
        c = gen_execution_times(n=5, w=500)
        assert set(c.keys()) == {1, 2, 3, 4, 5}

    def test_sum_approx_w(self):
        c = gen_execution_times(n=10, w=1000, round_c=False)
        assert sum(c.values()) == pytest.approx(1000, rel=0.01)

    def test_rounded_minimum_one(self):
        random.seed(42)
        c = gen_execution_times(n=10, w=1000, round_c=True)
        for v in c.values():
            assert v >= 1
            assert isinstance(v, int)

    def test_dummy_source_sink(self):
        c = gen_execution_times(n=8, w=500, round_c=True, dummy=True)
        assert c[1] == 1  # source
        assert c[8] == 1  # sink

    def test_dummy_keys(self):
        c = gen_execution_times(n=6, w=300, dummy=True)
        assert set(c.keys()) == {1, 2, 3, 4, 5, 6}

    def test_dummy_sum(self):
        random.seed(42)
        c = gen_execution_times(n=10, w=1000, round_c=False, dummy=True)
        # Sum should be close to w (source=1, sink=1, rest sums to w-2)
        assert sum(c.values()) == pytest.approx(1000, rel=0.01)


# ---- drs_gen ----

drs_mod = pytest.importorskip("drs")

class TestDrsGen:
    def test_returns_nsets(self):
        sets = drs_gen(n=5, u=1.0, nsets=3, ulimit=1)
        assert len(sets) == 3

    def test_each_set_has_n_elements(self):
        sets = drs_gen(n=6, u=1.5, nsets=2, ulimit=1)
        for s in sets:
            assert len(s) == 6

    def test_each_set_sums_to_u(self):
        sets = drs_gen(n=5, u=2.0, nsets=3, ulimit=2)
        for s in sets:
            assert sum(s) == pytest.approx(2.0)

    def test_respects_ulimit(self):
        sets = drs_gen(n=5, u=2.0, nsets=3, ulimit=1)
        for s in sets:
            for v in s:
                assert v <= 1.0 + 1e-9

    def test_all_values_non_negative(self):
        sets = drs_gen(n=5, u=1.0, nsets=3, ulimit=1)
        for s in sets:
            for v in s:
                assert v >= 0
