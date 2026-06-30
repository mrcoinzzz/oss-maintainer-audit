from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


DEFAULT_REQUIRED_FILES = {
    "README": ("README.md", "README.rst", "README.txt"),
    "License": ("LICENSE", "LICENSE.md", "COPYING"),
    "Contributing guide": ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
    "Code of conduct": ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
    "Security policy": ("SECURITY.md", ".github/SECURITY.md"),
    "Issue templates": (".github/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE.md"),
    "Pull request template": (".github/PULL_REQUEST_TEMPLATE.md",),
    "CI workflow": (".github/workflows",),
    "Changelog": ("CHANGELOG.md", "HISTORY.md", "RELEASES.md"),
    "Package metadata": ("pyproject.toml", "package.json", "Cargo.toml", "go.mod"),
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    message: str
    weight: int = 1


@dataclass(frozen=True)
class AuditResult:
    root: Path
    checks: tuple[CheckResult, ...]

    @property
    def passed(self) -> int:
        return sum(check.weight for check in self.checks if check.passed)

    @property
    def total(self) -> int:
        return sum(check.weight for check in self.checks)

    @property
    def score_percent(self) -> int:
        if self.total == 0:
            return 0
        return round((self.passed / self.total) * 100)


def audit_repository(
    root: Path | str,
    disabled_checks: Iterable[str] = (),
    required_files: Mapping[str, Iterable[str]] | None = None,
) -> AuditResult:
    repo_root = Path(root).expanduser().resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_root}")
    if not repo_root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repo_root}")

    disabled = set(disabled_checks)
    file_map = _required_file_map(required_files)
    checks = tuple(
        _check_any_file(repo_root, name, candidates)
        for name, candidates in file_map.items()
        if name not in disabled
    )

    return AuditResult(root=repo_root, checks=checks)


def _check_any_file(root: Path, name: str, candidates: Iterable[str]) -> CheckResult:
    for candidate in candidates:
        candidate_path = root / candidate
        if candidate_path.exists():
            return CheckResult(name=name, passed=True, message=f"{candidate} found")

    candidate_list = ", ".join(candidates)
    return CheckResult(name=name, passed=False, message=f"Add one of: {candidate_list}")


def _required_file_map(required_files: Mapping[str, Iterable[str]] | None) -> dict[str, tuple[str, ...]]:
    file_map = {name: tuple(candidates) for name, candidates in DEFAULT_REQUIRED_FILES.items()}
    if not required_files:
        return file_map

    for name, candidates in required_files.items():
        file_map[name] = tuple(candidates)
    return file_map
