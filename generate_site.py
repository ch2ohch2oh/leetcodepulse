#!/usr/bin/env python3
"""
Generates the static site (index.html) based on the indices configuration.
"""

import argparse
import sys
import yaml
from pathlib import Path


def load_config(config_path: str) -> dict:
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def parse_csv(file_path: str) -> list:
    data = []
    path = Path(file_path)
    if not path.exists():
        return data

    try:
        with open(path, "r") as f:
            lines = f.readlines()
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    try:
                        # Validate we can parse it, but store raw values for JS
                        # timestamp, total_users
                        data.append(
                            {"timestamp": parts[0], "total_users": int(parts[1])}
                        )
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error parseing {file_path}: {e}", file=sys.stderr)
    return data


def generate_html(indices: list, output_path: str):
    js_indices = []
    all_data = {}

    for idx in indices:
        # Indices info for dropdown
        js_indices.append({"id": idx.get("id"), "name": idx.get("name")})

        # Read data
        input_csv = idx.get("output_file", "")
        # The output_file in config is relative to project root, e.g. "data/leetcode75_stats.csv"
        # We run this script from project root, so strictly speaking it should work directly.
        # But if output_file is missing, we just pass empty list.

        all_data[idx.get("id")] = parse_csv(input_csv)

    # Read template from file
    template_path = Path("templates/template.html")
    # Inject JSON
    import json

    # Setup Jinja2 environment
    from jinja2 import Environment, FileSystemLoader

    # We want to load the template from its parent directory
    # template_path is "site/template.html" or absolute path.
    # Let's resolve the directory and filename.
    template_dir = template_path.parent
    template_name = template_path.name

    try:
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template(template_name)

        html_content = template.render(
            INDICES_JSON=json.dumps(js_indices), DATA_JSON=json.dumps(all_data)
        )
    except Exception as e:
        print(f"Error rendering template: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        out_path_obj = Path(output_path)
        out_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path_obj, "w") as f:
            f.write(html_content)
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error writing HTML: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate static site from indices config."
    )
    parser.add_argument(
        "-c", "--config", default="config/indices.yaml", help="Path to indices config"
    )
    parser.add_argument(
        "-o", "--output", default="public/index.html", help="Output HTML file path"
    )

    args = parser.parse_args()

    config = load_config(args.config)
    indices = config.get("indices", [])

    if not indices:
        print("No indices found in config.", file=sys.stderr)
        sys.exit(1)

    generate_html(indices, args.output)


if __name__ == "__main__":
    main()
