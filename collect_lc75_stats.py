#!/usr/bin/env python3
"""
Periodic collector for LeetCode 75 online user statistics.
Aggregates total online users across all problems and stores results in a CSV file.
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from leetcode_monitor import LeetCodeMonitor


def collect_stats(input_file: str, output_file: str, verbose: bool = False) -> dict:
    """
    Collect online user statistics for all problems in the input file.

    Args:
        input_file: Path to file containing problem slugs
        output_file: Path to CSV file for storing results
        verbose: Whether to print detailed progress

    Returns:
        dict: Statistics including timestamp, total_users, problems_checked, and errors
    """
    # Read problem slugs
    try:
        with open(input_file, "r") as f:
            slugs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"Checking {len(slugs)} problems...")

    # Collect online user counts
    total_users = 0
    successful_checks = 0
    failed_checks = 0

    for i, slug in enumerate(slugs, 1):
        count = LeetCodeMonitor.get_online_users(slug)

        if count >= 0:
            total_users += count
            successful_checks += 1
            if verbose:
                print(f"  [{i}/{len(slugs)}] {slug}: {count} users")
        else:
            failed_checks += 1
            if verbose:
                print(f"  [{i}/{len(slugs)}] {slug}: FAILED", file=sys.stderr)

    # Prepare statistics
    timestamp = datetime.now()
    stats = {
        "timestamp": timestamp,
        "total_users": total_users,
        "problems_checked": successful_checks,
        "problems_failed": failed_checks,
        "total_problems": len(slugs),
    }

    # Write to CSV
    file_exists = os.path.exists(output_file)

    try:
        with open(output_file, "a", newline="") as f:
            fieldnames = [
                "timestamp",
                "total_users",
                "problems_checked",
                "problems_failed",
                "total_problems",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(stats)

        if verbose:
            print(f"\n✓ Results saved to {output_file}")
            print(f"  Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Total online users: {total_users}")
            print(f"  Problems checked: {successful_checks}/{len(slugs)}")
            if failed_checks > 0:
                print(f"  Failed checks: {failed_checks}")

    except Exception as e:
        print(f"Error writing to CSV: {e}", file=sys.stderr)
        sys.exit(1)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Collect and aggregate LeetCode 75 online user statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use defaults
  %(prog)s -v                                 # Verbose output
  %(prog)s -o custom_stats.csv                # Custom output file
  %(prog)s -i data/custom_list.txt -v         # Custom input with verbose
  
Scheduling with cron:
  # Run every 15 minutes
  */15 * * * * cd /path/to/lcmonitor && ./collect_lc75_stats.py
  
  # Run every hour at minute 0
  0 * * * * cd /path/to/lcmonitor && ./collect_lc75_stats.py
        """,
    )

    # Default paths relative to script location
    script_dir = Path(__file__).parent.absolute()
    default_input = script_dir / "data" / "leetcode75.txt"
    default_output = script_dir / "data" / "lc75_stats.csv"

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=str(default_input),
        metavar="FILE",
        help=f"input file containing problem slugs (default: {default_input})",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(default_output),
        metavar="FILE",
        help=f"output CSV file for statistics (default: {default_output})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print detailed progress information",
    )

    args = parser.parse_args()

    # Collect and save statistics
    collect_stats(args.input, args.output, args.verbose)


if __name__ == "__main__":
    main()
