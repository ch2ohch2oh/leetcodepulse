# LeetCode 75 Index

A monitoring system that tracks online user activity across all 75 problems in the LeetCode 75 study plan. The index aggregates the total number of users currently viewing these problems.

## 🚀 Live Demo

View the live dashboard: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

## 📊 Features

- **Automated data collection** via GitHub Actions (runs hourly)
- **Interactive dashboard** with time-series visualization
- **GitHub Pages deployment** - no server required
- **EST timezone** for consistent data recording

## Scripts

### 1. `leetcode_monitor.py`
Core monitoring class and CLI tool to check online users for individual problems.

**Usage:**
```bash
# Use default data/leetcode75.txt
./leetcode_monitor.py

# Use custom input file
./leetcode_monitor.py -i custom_problems.txt

# View help
./leetcode_monitor.py --help
```

### 2. `collect_lc75_stats.py`
Periodic data collection script that aggregates total online users across all LeetCode 75 problems and logs results to a CSV file with timestamps.

**Usage:**
```bash
# Run once with verbose output
./collect_lc75_stats.py -v

# Run quietly (for cron jobs)
./collect_lc75_stats.py

# Custom output file
./collect_lc75_stats.py -o custom_stats.csv

# View help
./collect_lc75_stats.py --help
```

**Output Format:**
The CSV file contains the following columns:
- `timestamp`: Date and time of data collection
- `total_users`: Sum of online users across all problems
- `problems_checked`: Number of problems successfully checked
- `problems_failed`: Number of problems that failed to check
- `total_problems`: Total number of problems in the input file

### 3. `get_leetcode75.py`
Fetches the current list of LeetCode 75 problems from the LeetCode API and saves them to `data/leetcode75.txt`.

**Usage:**
```bash
./get_leetcode75.py
```

## GitHub Pages Deployment

This project is designed to run as a static site on GitHub Pages with automated data collection via GitHub Actions.

**📖 See [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) for complete deployment instructions.**

Quick start:
1. Push this repository to GitHub
2. Enable GitHub Pages (Settings → Pages → Source: GitHub Actions)
3. Enable GitHub Actions and run the workflow
4. Your dashboard will be live at `https://YOUR_USERNAME.github.io/YOUR_REPO/`

The GitHub Action will automatically:
- Collect data every hour
- Update the CSV file
- Deploy the latest dashboard

## Local Development Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Make scripts executable:**
```bash
chmod +x leetcode_monitor.py collect_lc75_stats.py get_leetcode75.py
```

## Scheduling Periodic Collection

To automatically collect statistics at regular intervals, use cron:

```bash
# Edit crontab
crontab -e

# Add one of these lines:

# Run every 15 minutes
*/15 * * * * cd /Users/dazhi/code/lcmonitor && source venv/bin/activate && ./collect_lc75_stats.py

# Run every hour at minute 0
0 * * * * cd /Users/dazhi/code/lcmonitor && source venv/bin/activate && ./collect_lc75_stats.py

# Run every day at 9 AM
0 9 * * * cd /Users/dazhi/code/lcmonitor && source venv/bin/activate && ./collect_lc75_stats.py
```

**Note:** Make sure to use absolute paths in cron jobs and activate the virtual environment.

## Data Files

- `data/leetcode75.txt`: List of LeetCode 75 problem slugs (one per line)
- `data/lc75_stats.csv`: Historical statistics (created by `collect_lc75_stats.py`)

## Requirements

- Python 3.7+
- `requests>=2.31.0`
- `websocket-client>=1.7.0`

## Example Output

### Individual Problem Monitoring
```
$ ./leetcode_monitor.py
Loaded 75 problems from /Users/dazhi/code/lcmonitor/data/leetcode75.txt

Problem: merge-strings-alternately                          | Online Users: 136
Problem: greatest-common-divisor-of-strings                 | Online Users: 97
Problem: container-with-most-water                          | Online Users: 360
...
```

### Aggregate Statistics Collection
```
$ ./collect_lc75_stats.py -v
Checking 75 problems...
  [1/75] merge-strings-alternately: 124 users
  [2/75] greatest-common-divisor-of-strings: 103 users
  ...
  [75/75] online-stock-span: 52 users

✓ Results saved to /Users/dazhi/code/lcmonitor/data/lc75_stats.csv
  Timestamp: 2026-01-29 21:11:13
  Total online users: 5706
  Problems checked: 75/75
```

### CSV Output
```csv
timestamp,total_users,problems_checked,problems_failed,total_problems
2026-01-29 21:11:13.608232,5706,75,0,75
2026-01-29 21:12:25.207147,5736,75,0,75
```

## License

MIT
