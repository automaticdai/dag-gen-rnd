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
        assert "global" in config
        assert "dag_config" in config
        assert config["global"]["rnd_seed"] == 42

    def test_missing_file(self, tmp_path):
        with pytest.raises(EnvironmentError):
            parse_configuration(str(tmp_path / "nonexistent.json"))


class TestMainSingleDag:
    def test_single_dag_generation(self, tmp_path, sample_config):
        """End-to-end single-DAG generation with save disabled."""
        sample_config["global"]["multi-DAG_on"] = False
        sample_config["global"]["save_to_file"] = False
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
        sample_config["global"]["multi-DAG_on"] = False
        sample_config["global"]["save_to_file"] = True
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
        sample_config["global"]["multi-DAG_on"] = True
        sample_config["global"]["save_to_file"] = True
        sample_config["multi-DAG"]["set_number"] = 2
        sample_config["multi-DAG"]["task_number_per_set"] = 2

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config))
        data_dir = tmp_path / "data"

        main(config_path=str(config_path), data_path=str(data_dir))

        assert data_dir.exists()


class TestParseArgs:
    def test_defaults(self):
        config_path, data_path = _cli.parse_args([])
        assert config_path is None
        assert data_path is None

    def test_short_flags(self):
        assert _cli.parse_args(["-c", "a.json", "-d", "out"]) == ("a.json", "out")

    def test_long_flags(self):
        assert _cli.parse_args(["--config=a.json", "--directory=out"]) == ("a.json", "out")


class TestDirectoryFlag:
    def test_cli_writes_to_directory(self, tmp_path, sample_config):
        """Running the script with -d creates the output directory there."""
        import subprocess, sys
        config_path = tmp_path / "config.json"
        sample_config["single-DAG"]["set_number"] = 1
        config_path.write_text(json.dumps(sample_config))
        out_dir = tmp_path / "custom_out"

        script = os.path.join(os.path.dirname(__file__), os.pardir, "src", "daggen-cli.py")
        result = subprocess.run(
            [sys.executable, script, "-c", str(config_path), "-d", str(out_dir)],
            capture_output=True, text=True)

        assert result.returncode == 0, result.stderr
        assert out_dir.is_dir()


class TestAlgorithmConfig:
    @pytest.fixture
    def seen(self, monkeypatch):
        recorded = []

        for name in ("generate_dag", "generate_multi_dag_taskset"):
            original = getattr(_cli, name)

            def spy(*args, _orig=original, **kwargs):
                recorded.append(kwargs.get("algorithm"))
                return _orig(*args, **kwargs)

            monkeypatch.setattr(_cli, name, spy)
        return recorded

    def _run(self, tmp_path, config):
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))
        main(config_path=str(config_path), data_path=str(tmp_path / "data"))

    def test_single_dag_uses_configured_algorithm(self, tmp_path, sample_config, seen):
        sample_config["single-DAG"]["set_number"] = 2
        sample_config["dag_config"]["algorithm"] = "nfj"
        self._run(tmp_path, sample_config)
        assert seen == ["nfj", "nfj"]

    def test_multi_dag_uses_configured_algorithm(self, tmp_path, sample_config, seen):
        sample_config["global"]["multi-DAG_on"] = True
        sample_config["dag_config"]["algorithm"] = "legacy"
        self._run(tmp_path, sample_config)
        assert seen == ["legacy"]

    def test_algorithm_defaults_to_rnd(self, tmp_path, sample_config, seen):
        sample_config["single-DAG"]["set_number"] = 1
        self._run(tmp_path, sample_config)
        assert seen == ["rnd"]
