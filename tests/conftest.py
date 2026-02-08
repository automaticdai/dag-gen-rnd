import pytest
import json


@pytest.fixture
def sample_config():
    """Returns a minimal valid config dict."""
    return {
        "misc": {
            "multi-DAG_on": False,
            "cores": 4,
            "print_DAG": False,
            "save_to_file": False,
            "dummy_source_and_sink": False,
            "rnd_seed": 42,
            "util_algorithm": "uunifast_discard"
        },
        "multi-DAG": {
            "set_number": 2,
            "task_number_per_set": 3,
            "utilization": 0.8,
            "periods": [1000, 2000, 5000]
        },
        "single-DAG": {
            "set_number": 5,
            "workload": 10000
        },
        "dag_config": {
            "parallelism": 4,
            "layer_num_min": 3,
            "layer_num_max": 6,
            "connect_prob": 0.5
        }
    }


@pytest.fixture
def config_file(tmp_path, sample_config):
    """Writes sample config to a temp file and returns its path."""
    p = tmp_path / "config.json"
    p.write_text(json.dumps(sample_config))
    return str(p)


@pytest.fixture
def multi_dag_config_file(tmp_path, sample_config):
    """Config file with multi-DAG mode enabled."""
    sample_config["misc"]["multi-DAG_on"] = True
    sample_config["misc"]["save_to_file"] = True
    p = tmp_path / "config_multi.json"
    p.write_text(json.dumps(sample_config))
    return str(p)
