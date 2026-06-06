from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import AuditResult, audit_repository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="oss-maintainer-audit",
        description="Audit a repository for public open-source maintenance signals.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path to audit")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )

    args = parser.parse_args(argv)

    try:
        result = audit_repository(Path(args.path))
    except (FileNotFoundError, NotADirectoryError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        print(_to_json(result))
    else:
        print(_to_text(result))

    return 0 if result.score_percent >= 70 else 1


def _to_text(result: AuditResult) -> str:
    lines = [
        f"OSS Maintainer Audit: {result.root}",
        "",
        f"Score: {result.passed}/{result.total} ({result.score_percent}%)",
        "",
    ]

    for check in result.checks:
        status = "PASS" if check.passed else "WARN"
        lines.append(f"{status:<5} {check.name:<22} {check.message}")

    return "\n".join(lines)


def _to_json(result: AuditResult) -> str:
    payload = {
        "root": str(result.root),
        "score": {
            "passed": result.passed,
            "total": result.total,
            "percent": result.score_percent,
        },
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
                "weight": check.weight,
            }
            for check in result.checks
        ],
    }
    return json.dumps(payload, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
