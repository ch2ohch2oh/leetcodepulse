#!/usr/bin/env python3
"""Minimal LeetCode GraphQL client used by the collector."""

import sys
import time

import requests


class LeetCodeClient:
    """Fetch the cumulative submission count for a LeetCode problem."""

    GRAPHQL_URL = "https://leetcode.com/graphql"

    @classmethod
    def get_total_submissions(cls, title_slug: str, max_attempts: int = 3) -> int | None:
        query = """
        query questionTitle($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            stats
          }
        }
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        }
        payload = {"query": query, "variables": {"titleSlug": title_slug}}

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(
                    cls.GRAPHQL_URL,
                    json=payload,
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()

                response_data = response.json()
                question = response_data.get("data", {}).get("question")
                if not question or not question.get("stats"):
                    raise ValueError("response did not contain question statistics")

                stats = question["stats"]
                import json

                return int(json.loads(stats)["totalSubmissionRaw"])
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                if attempt == max_attempts:
                    print(
                        f"Unable to fetch submissions for {title_slug}: {exc}",
                        file=sys.stderr,
                    )
                    return None
                time.sleep(2 ** (attempt - 1))

        return None
