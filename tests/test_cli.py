import pytest
import os
import json
import importlib

# daggen-cli.py has a hyphen, so we need importlib to import it
_cli = importlib.import_module("daggen-cli")
parse_configuration = _cli.parse_configuration
main = _cli.main


class TestParseConfiguration:
    def test_valid_config(self, config_file):
        config = parse_configuration(config_file)
        assert "misc" in config
        assert "dag_config" in config
        assert config["misc"]["rnd_seed"] == 42

    def test_missing_file(self, tmp_path):
        with pytest.raises(EnvironmentError):
            parse_configuration(str(tmp_path / "nonexistent.json"))


class TestMainSingleDag:
    def test_single_dag_generation(self, tmp_path, sample_config):
        """End-to-end single-DAG generation with save disabled."""
        sample_config["misc"]["multi-DAG_on"] = False
        sample_config["misc"]["save_to_file"] = False
        sample_config["single-DAG"]["set_number"] = 3

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))

        # Should complete without error
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))

    @pytest.fixture(autouse=False)
    def _skip_if_no_pygraphviz(self):
        pytest.importorskip("pygraphviz")

    def test_single_dag_with_save(self, tmp_path, sample_config, _skip_if_no_pygraphviz):
        """End-to-end single-DAG generation with file saving."""
        sample_config["misc"]["multi-DAG_on"] = False
        sample_config["misc"]["save_to_file"] = True
        sample_config["single-DAG"]["set_number"] = 2

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        data_dir = tmp_path / "data"

        main(config_path=str(config_path), data_path=str(data_dir))

        assert data_dir.exists()
        # Should have files for Tau_0 and Tau_1
        assert (data_dir / "Tau_0.gml").exists()
        assert (data_dir / "Tau_1.gml").exists()


class TestMainMultiDag:
    @pytest.fixture(autouse=False)
    def _skip_if_no_pygraphviz(self):
        pytest.importorskip("pygraphviz")

    def test_multi_dag_with_save(self, tmp_path, sample_config, _skip_if_no_pygraphviz):
        """End-to-end multi-DAG generation with file saving."""
        sample_config["misc"]["multi-DAG_on"] = True
        sample_config["misc"]["save_to_file"] = True
        sample_config["multi-DAG"]["set_number"] = 2
        sample_config["multi-DAG"]["task_number_per_set"] = 2

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        data_dir = tmp_path / "data"

        main(config_path=str(config_path), data_path=str(data_dir))

        assert data_dir.exists()
