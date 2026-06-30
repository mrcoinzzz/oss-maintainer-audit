from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_CONFIG_FILES = (".oss-maintainer-audit.json",)


@dataclass(frozen=True)
class AuditConfig:
    min_score: int | None = None
    disabled_checks: tuple[str, ...] = ()
    required_files: dict[str, tuple[str, ...]] = field(default_factory=dict)


def load_config(repo_root: Path, explicit_path: str | None = None) -> AuditConfig:
    config_path = _resolve_config_path(repo_root, explicit_path)
    if config_path is None:
        return AuditConfig()

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in config file {config_path}: {error}") from error

    if not isinstance(raw, dict):
        raise ValueError(f"Config file must contain a JSON object: {config_path}")

    return AuditConfig(
        min_score=_optional_int(raw.get("min_score"), "min_score"),
        disabled_checks=_string_tuple(raw.get("disabled_checks", ()), "disabled_checks"),
        required_files=_required_files(raw.get("required_files", {})),
    )


def _resolve_config_path(repo_root: Path, explicit_path: str | None) -> Path | None:
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if not path.is_absolute():
            path = repo_root / path
        if not path.exists():
            raise FileNotFoundError(f"Config file does not exist: {path}")
        return path

    for filename in DEFAULT_CONFIG_FILES:
        path = repo_root / filename
        if path.exists():
            return path
    return None


def _optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"Config field {name} must be an integer")
    return value


def _string_tuple(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"Config field {name} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"Config field {name} must be a list of strings")
    return tuple(value)


def _required_files(value: object) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, dict):
        raise ValueError("Config field required_files must be an object")

    result: dict[str, tuple[str, ...]] = {}
    for name, candidates in value.items():
        if not isinstance(name, str):
            raise ValueError("Config field required_files keys must be strings")
        result[name] = _string_tuple(candidates, f"required_files.{name}")
    return result
