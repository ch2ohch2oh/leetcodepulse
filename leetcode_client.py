#!/usr/bin/env python3
import time
import random
import sys
import websocket
import requests


class LeetCodeMonitor:
    """Monitor for tracking online users viewing LeetCode problems."""

    BASE_URI = "wss://collaboration-ws.leetcode.com/problems/{}"

    @classmethod
    def get_question_stats(cls, title_slug: str) -> dict:
        """
        Fetches the submission and accepted counts for a question using GraphQL.

        Args:
            title_slug (str): The URL slug of the question.

        Returns:
            dict: A dictionary containing 'totalAccepted' and 'totalSubmission' (raw integers),
                  or None if the request fails.
        """
        url = "https://leetcode.com/graphql"
        query = """
        query questionTitle($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            stats
          }
        }
        """
        variables = {"titleSlug": title_slug}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        }

        try:
            response = requests.post(
                url,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=10,
            )

            if response.status_code != 200:
                print(
                    f"Request failed for {title_slug} with status code {response.status_code}",
                    file=sys.stderr,
                )
                return None

            data = response.json()
            if (
                "data" in data
                and "question" in data["data"]
                and data["data"]["question"]
            ):
                stats_str = data["data"]["question"].get("stats")
                if stats_str:
                    import json

                    stats = json.loads(stats_str)
                    return {
                        "totalAccepted": stats.get("totalAcceptedRaw", 0),
                        "totalSubmission": stats.get("totalSubmissionRaw", 0),
                    }
            return None

        except Exception as e:
            print(
                f"An error occurred fetching stats for {title_slug}: {e}",
                file=sys.stderr,
            )
            return None

    @classmethod
    def get_online_users(cls, problem_slug: str) -> int:
        """
        [DEPRECATED] Connects to LeetCode's collaboration WebSocket to retrieve the number of online users.
        NOTE: This is often blocked by Cloudflare (403 Forbidden) on cloud environments.
        """
        uri = cls.BASE_URI.format(problem_slug)

        # Enhanced headers to mimic a real browser more closely
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://leetcode.com",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Fetch-Dest": "websocket",
            "Sec-Fetch-Mode": "websocket",
            "Sec-Fetch-Site": "same-site",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to appear more human-like
                if attempt > 0:
                    delay = (2**attempt) + random.uniform(0, 1)
                    time.sleep(delay)

                # Create WebSocket connection
                ws = websocket.create_connection(uri, header=headers, timeout=15)

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
                if attempt == max_retries - 1:
                    # Last attempt failed
                    error_msg = str(e)
                    if "403 Forbidden" in error_msg:
                        print(
                            f"Error fetching online users for {problem_slug}: Cloudflare blocked the request (403 Forbidden). "
                            "This often happens on GCP/cloud environments due to IP reputation or bot detection."
                        )
                    else:
                        print(f"Error fetching online users for {problem_slug}: {e}")
                    return -1
                # Otherwise, retry
                continue

        return -1


def get_study_plan_problems(plan_slug: str):
    """
    Fetches the list of problem title slugs from a LeetCode study plan.

    Args:
        plan_slug (str): The slug of the study plan (e.g., 'leetcode-75', 'top-interview-150').

    Returns:
        list: A list of title slugs for all problems in the plan.
    """
    url = "https://leetcode.com/graphql"
    query = """
    query studyPlanV2Detail($slug: String!) {
      studyPlanV2Detail(planSlug: $slug) {
        planSubGroups {
          questions {
            titleSlug
          }
        }
      }
    }
    """
    variables = {"slug": plan_slug}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Referer": f"https://leetcode.com/studyplan/{plan_slug}/",
    }

    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            print(
                f"Request failed with status code {response.status_code}",
                file=sys.stderr,
            )
            return []

        data = response.json()
        questions = []
        if "data" in data and "studyPlanV2Detail" in data["data"]:
            detail = data["data"]["studyPlanV2Detail"]
            if detail and "planSubGroups" in detail:
                for group in detail["planSubGroups"]:
                    if "questions" in group:
                        for question in group["questions"]:
                            if "titleSlug" in question:
                                questions.append(question["titleSlug"])
        return questions

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    import argparse
    import os
    import sys

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Interact with LeetCode: Monitor users or fetch study plans.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor users (existing behavior)
  %(prog)s
  %(prog)s -i custom_problems.txt

  # Fetch study plan
  %(prog)s --fetch-plan leetcode-75 -o data/leetcode75.txt
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
        help=f"input file containing problem slugs for monitoring (default: {default_input})",
    )

    parser.add_argument(
        "--fetch-plan",
        type=str,
        metavar="SLUG",
        help="fetch problems from a study plan slug (e.g. leetcode-75)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="OUT_FILE",
        help="output file to save fetched problems",
    )

    args = parser.parse_args()

    # Mode 1: Fetch Plan
    if args.fetch_plan:
        print(f"Fetching problems for study plan: {args.fetch_plan}...")
        slugs = get_study_plan_problems(args.fetch_plan)

        if not slugs:
            print("No problems found or error occurred.")
            sys.exit(1)

        print(f"Found {len(slugs)} problems.")

        if args.output:
            # Create output directory if needed
            output_dir = os.path.dirname(os.path.abspath(args.output))
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(args.output, "w") as f:
                for slug in slugs:
                    f.write(slug + "\n")
            print(f"Saved to {args.output}")
        else:
            print("First 5 problems:")
            for s in slugs[:5]:
                print(f"  - {s}")

        sys.exit(0)

    # Mode 2: Monitor Users
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
