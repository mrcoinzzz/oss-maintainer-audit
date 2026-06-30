from pathlib import Path

from oss_maintainer_audit.config import load_config


def test_load_config_reads_default_file(tmp_path: Path) -> None:
    (tmp_path / ".oss-maintainer-audit.json").write_text(
        """
        {
          "min_score": 80,
          "disabled_checks": ["Code of conduct"],
          "required_files": {
            "README": ["docs/overview.md"]
          }
        }
        """,
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.min_score == 80
    assert config.disabled_checks == ("Code of conduct",)
    assert config.required_files == {"README": ("docs/overview.md",)}


def test_load_config_returns_empty_config_when_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path)

    assert config.min_score is None
    assert config.disabled_checks == ()
    assert config.required_files == {}
