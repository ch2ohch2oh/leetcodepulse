#!/usr/bin/env python3
"""Generate the static Two Sum Pulse dashboard."""

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parent


def load_config(config_path: Path) -> dict:
    try:
        with config_path.open() as config_file:
            return yaml.safe_load(config_file) or {}
    except (OSError, yaml.YAMLError) as exc:
        print(f"Unable to load {config_path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def parse_csv(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []

    data = []
    try:
        with file_path.open() as source:
            for row in csv.DictReader(source):
                timestamp = row.get("timestamp")
                total = row.get("total_submissions")
                if not timestamp or total is None:
                    continue
                try:
                    data.append(
                        {"timestamp": timestamp, "total_submissions": int(total)}
                    )
                except ValueError:
                    continue
    except OSError as exc:
        print(f"Unable to parse {file_path}: {exc}", file=sys.stderr)
    return data


def generate_html(config: dict, output_path: Path) -> None:
    problem = config.get("problem", {})
    data_file = problem.get("output_file")
    if not data_file:
        raise ValueError("config must define problem.output_file")

    data_path = Path(data_file)
    if not data_path.is_absolute():
        data_path = PROJECT_ROOT / data_path

    env = Environment(loader=FileSystemLoader(str(PROJECT_ROOT / "templates")))
    template = env.get_template("template.html")
    html = template.render(
        DATA_JSON=json.dumps(parse_csv(data_path)),
    )

    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"Successfully generated {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config" / "indices.yaml",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("public/index.html"))
    args = parser.parse_args()

    try:
        generate_html(load_config(args.config), args.output)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
