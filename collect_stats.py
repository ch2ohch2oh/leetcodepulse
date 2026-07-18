#!/usr/bin/env python3
"""Collect the cumulative Two Sum submission count."""

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from leetcode_client import LeetCodeClient


PROJECT_ROOT = Path(__file__).resolve().parent


def load_config(config_path: Path) -> dict:
    try:
        with config_path.open() as config_file:
            return yaml.safe_load(config_file) or {}
    except (OSError, yaml.YAMLError) as exc:
        print(f"Unable to load {config_path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def collect(config: dict, verbose: bool = False) -> dict:
    problem = config.get("problem", {})
    slug = problem.get("slug")
    output_file = problem.get("output_file")
    if not slug or not output_file:
        raise ValueError("config must define problem.slug and problem.output_file")

    total_submissions = LeetCodeClient.get_total_submissions(slug)
    if total_submissions is None:
        raise RuntimeError("collection failed; no sample was written")

    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_submissions": total_submissions,
    }
    file_exists = output_path.exists()
    with output_path.open("a", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    if verbose:
        print(f"Two Sum total submissions: {total_submissions:,}")
        print(f"Saved sample to {output_path}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config" / "indices.yaml",
        help="path to the collector configuration",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    try:
        collect(load_config(args.config), args.verbose)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
