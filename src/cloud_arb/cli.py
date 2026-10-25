"""Command-line interface for the Cloud Arbitrage Orchestrator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from . import __version__
from .models import WorkloadSpec
from .orchestrator import Orchestrator


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cloud-arb",
        description="Multi-Cloud Arbitrage Engine.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"cloud-arb {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the arbitrage analysis.")
    run.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Path to workload config YAML.",
    )
    run.add_argument(
        "--pricing",
        default=Path("examples/mock-pricing.json"),
        type=Path,
        help="Path to pricing data JSON.",
    )
    run.add_argument(
        "--workdir",
        default=Path("out"),
        type=Path,
        help="Directory for generated IaC (default: ./out).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "run":
        parser.print_help()
        sys.exit(2)

    if not args.config.exists():
        print(f"[ERROR] Config not found: {args.config}", file=sys.stderr)
        sys.exit(2)

    try:
        data = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        spec = WorkloadSpec(**data)
    except (TypeError, yaml.YAMLError) as exc:
        print(f"[ERROR] Invalid config: {exc}", file=sys.stderr)
        sys.exit(2)

    orchestrator = Orchestrator(args.workdir, args.pricing)
    sys.exit(orchestrator.run(spec))


if __name__ == "__main__":
    main()
