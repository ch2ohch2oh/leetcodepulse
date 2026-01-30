#!/usr/bin/env python3
import requests


def get_leetcode75_slugs():
    """
    Fetches the list of problem title slugs from the LeetCode 75 study plan.

    Returns:
        list: A list of title slugs for all problems in the LeetCode 75 study plan.
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
    variables = {"slug": "leetcode-75"}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Referer": "https://leetcode.com/studyplan/leetcode-75/",
    }

    payload = {"query": query, "variables": variables}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            return []

        data = response.json()

        # Parse the response to extract title slugs
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

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    import os

    slugs = get_leetcode75_slugs()
    if slugs:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Save to file
        output_file = "data/leetcode75.txt"
        with open(output_file, "w") as f:
            for slug in slugs:
                f.write(slug + "\n")

        print(
            f"Successfully retrieved {len(slugs)} title slugs and saved to {output_file}"
        )
        print("\nFirst 10 problems:")
        for slug in slugs[:10]:
            print(f"  - {slug}")
    else:
        print("Failed to retrieve slugs.")
