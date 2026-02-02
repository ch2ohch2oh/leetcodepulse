#!/usr/bin/env python3
"""
Generic collector for LeetCode online user statistics.
Reads configuration from config/indices.yaml and collects stats for defined indices.
"""

import argparse
import csv
import os
import sys
import time
import random
import yaml
from datetime import datetime, timezone
from pathlib import Path

from leetcode_client import LeetCodeMonitor


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)


def collect_index_stats(index_config: dict, verbose: bool = False) -> dict:
    """
    Collect statistics for a single index configuration.

    Args:
        index_config: Dictionary containing 'input_file' and 'output_file' (and optional 'name')
        verbose: Whether to print detailed progress

    Returns:
        dict: Statistics for this index run
    """
    input_file = index_config.get("input_file")
    output_file = index_config.get("output_file")
    index_name = index_config.get("name", "Unknown Index")

    if not input_file or not output_file:
        print(
            f"Error: Invalid config for index '{index_name}'. Missing input or output file.",
            file=sys.stderr,
        )
        return {}

    # Resolve paths relative to project root if they are relative
    # Assuming script is in root or we use absolute paths in config.
    # For now, let's assume paths are relative to the project root (where the script runs).

    if verbose:
        print(f"Processing Index: {index_name}")

    # Read problem slugs
    try:
        with open(input_file, "r") as f:
            slugs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        return {"error": "Input file not found"}

    if verbose:
        print(f"  Checking {len(slugs)} problems...")

    # Collect stats

    total_accepted = 0
    total_submissions = 0
    successful_checks = 0
    failed_checks = 0

    for i, slug in enumerate(slugs, 1):
        # Add small random delay to avoid rate limiting
        # Only sleep if checking multiple items and it's not the first one
        if i > 1:
            time.sleep(random.uniform(0.5, 1.5))

        stats = LeetCodeMonitor.get_question_stats(slug)

        if stats:
            total_accepted += stats.get("totalAccepted", 0)
            total_submissions += stats.get("totalSubmission", 0)
            successful_checks += 1
            if verbose:
                print(f"    [{i}/{len(slugs)}] {slug}: Success")
        else:
            failed_checks += 1
            if verbose:
                print(f"    [{i}/{len(slugs)}] {slug}: FAILED", file=sys.stderr)

    # Prepare statistics
    timestamp = datetime.now(timezone.utc)
    stats_row = {
        "timestamp": timestamp,
        "live_users": 0,  # No longer collecting live users
        "problems_checked": successful_checks,
        "problems_failed": failed_checks,
        "total_problems": len(slugs),
        "total_accepted": total_accepted,
        "total_submissions": total_submissions,
    }

    # Write to CSV
    file_exists = os.path.exists(output_file)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, "a", newline="") as f:
            fieldnames = [
                "timestamp",
                "live_users",
                "problems_checked",
                "problems_failed",
                "total_problems",
                "total_accepted",
                "total_submissions",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(stats_row)

        if verbose:
            print(f"  ✓ Results saved to {output_file}")
            print(f"  Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S%z')}")
            print(f"  Total accepted: {total_accepted}")
            print(f"  Total submissions: {total_submissions}")
            print(f"  Problems checked: {successful_checks}/{len(slugs)}")
            if failed_checks > 0:
                print(f"  Failed checks: {failed_checks}")
            print("-" * 40)

    except Exception as e:
        print(f"Error writing to CSV: {e}", file=sys.stderr)

    return stats_row


def main():
    parser = argparse.ArgumentParser(
        description="Collect online user statistics for defined indices.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    script_dir = Path(__file__).parent.absolute()
    default_config = script_dir / "config" / "indices.yaml"

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=str(default_config),
        help=f"path to configuration file (default: {default_config})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print detailed progress information",
    )

    parser.add_argument(
        "--index", type=str, help="specific index ID to process (optional)"
    )

    # If no arguments provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    config = load_config(args.config)
    indices = config.get("indices", [])

    if not indices:
        print("No indices defined in configuration.")
        return

    processed_count = 0
    for index_config in indices:
        # If --index is specified, only process matching index
        if args.index and index_config.get("id") != args.index:
            continue

        collect_index_stats(index_config, args.verbose)
        processed_count += 1

    if args.index and processed_count == 0:
        print(f"Warning: Index with ID '{args.index}' not found in config.")


if __name__ == "__main__":
    main()
