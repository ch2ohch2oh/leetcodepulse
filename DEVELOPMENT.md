# Development Guidelines

This project requires a specific Python environment setup and includes several scripts for data collection and site generation.

## Virtual Environment (venv)

**CRITICAL:** This project uses a local virtual environment named `venv`.

*   **Always** use the python executable from the virtual environment.
*   **Do not** use the system global python.

### Running Scripts

You have two options:

1.  **Activate the environment first (Recommended for shells):**
    ```bash
    source venv/bin/activate
    python collect_stats.py
    ```

2.  **Use the direct path:**
    ```bash
    ./venv/bin/python collect_stats.py
    ```

## Scripts Overview

### 1. `leetcode_client.py`
Handles WebSocket connections to LeetCode's collaboration service and fetches study plans.

**Usage:**
```bash
# Basic usage
./leetcode_client.py

# Fetch LeetCode 75 (default)
./leetcode_client.py --fetch-plan leetcode-75

# Fetch another plan and save to file
./leetcode_client.py --fetch-plan top-interview-150 -o data/top_150.txt
```

### 2. `collect_stats.py`
Aggregates total online users across configured indices and logs to CSV.

**Usage:**
```bash
# Run with default config
./collect_stats.py

# Run with verbose output
./collect_stats.py -v
```

**Output Format (CSV):**
`timestamp, total_users, problems_checked, problems_failed, total_problems`

### 3. `generate_site.py`
Generates the dashboard visualization in `public/index.html`.

**Usage:**
```bash
./venv/bin/python generate_site.py
```

## Automation (Cron)

To automatically collect statistics, add a entry to your crontab (`crontab -e`):

```bash
# Run every 15 minutes
*/15 * * * * cd /path/to/lcmonitor && source venv/bin/activate && ./collect_stats.py
```

---

## Technical Details

### Dependencies
- Python 3.7+
- `requests>=2.31.0`
- `websocket-client>=1.7.0`

### Data Files
- `data/leetcode75_problems.txt`: List of problem slugs.
- `data/leetcode75_stats.csv`: Historical statistics.
- `templates/template.html`: Dashboard template.
- `public/index.html`: Generated dashboard (local build).
