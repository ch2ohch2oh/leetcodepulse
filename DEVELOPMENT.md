# Development

## Setup

Create a virtual environment named `venv` and install the dependencies:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Collect a sample

```bash
venv/bin/python collect_stats.py -v
```

The collector makes one GraphQL request for Two Sum's cumulative submission
count. It retries transient failures and writes nothing if all attempts fail.

CSV format:

```text
timestamp,total_submissions
```

The active problem and output file are configured in `config/indices.yaml`.

## Generate the site

```bash
venv/bin/python generate_site.py
```

The generated dashboard is written to `public/index.html`.

## Run both steps

```bash
./update_site.sh
```

## Automation

`cron.sh` pulls `main`, collects a sample, commits the updated CSV, and pushes
it. The GitHub Pages workflow then generates and deploys the static site.

For example, to collect hourly:

```cron
1 * * * * cd /path/to/leetcodepulse && ./cron.sh >> pulse.log 2>&1
```
