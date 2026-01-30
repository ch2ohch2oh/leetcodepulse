#!/usr/bin/env python3
import websocket


class LeetCodeMonitor:
    """Monitor for tracking online users viewing LeetCode problems."""

    BASE_URI = "wss://collaboration-ws.leetcode.com/problems/{}"

    @classmethod
    def get_online_users(cls, problem_slug: str) -> int:
        """
        Connects to LeetCode's collaboration WebSocket to retrieve the number of online users
        viewing a specific problem.

        Args:
            problem_slug (str): The URL slug of the problem (e.g., 'two-sum').

        Returns:
            int: The number of online users, or -1 if an error occurs.
        """
        uri = cls.BASE_URI.format(problem_slug)

        # Custom headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "Origin": "https://leetcode.com",
        }

        try:
            # Create WebSocket connection
            ws = websocket.create_connection(uri, header=headers, timeout=10)

            try:
                # The server pushes a raw string representing the count on connection
                message = ws.recv()

                # Try to interpret the result as an integer
                try:
                    return int(message)
                except ValueError:
                    # If slightly different format
                    print(f"Received unexpected format: {message}")
                    return -1
            finally:
                ws.close()

        except Exception as e:
            print(f"Error fetching online users for {problem_slug}: {e}")
            return -1


if __name__ == "__main__":
    import argparse
    import os
    import sys

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Monitor online users viewing LeetCode problems.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Use default data/leetcode75.txt
  %(prog)s -i custom_problems.txt       # Use custom input file
  %(prog)s --input data/my_list.txt     # Use custom input file (long form)
        """,
    )

    # Default to data/leetcode75.txt relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, "data", "leetcode75.txt")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=default_input,
        metavar="FILE",
        help=f"input file containing problem slugs (default: {default_input})",
    )

    args = parser.parse_args()

    # Read problem slugs from file
    try:
        with open(args.input, "r") as f:
            slugs = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(slugs)} problems from {args.input}\n")

        for slug in slugs:
            count = LeetCodeMonitor.get_online_users(slug)
            print(f"Problem: {slug:50} | Online Users: {count}")

    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
