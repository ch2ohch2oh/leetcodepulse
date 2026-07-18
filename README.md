# Two Sum Pulse

A tiny activity monitor for LeetCode. It uses the number of new submissions to
[Two Sum](https://leetcode.com/problems/two-sum/) as a simple, recognizable pulse
of coding activity.

## Live dashboard

[View Two Sum Pulse](https://ch2ohch2oh.github.io/leetcodepulse/)

The dashboard groups new Two Sum submissions into completed calendar hours,
days, weeks, or months. Times are shown in the viewer's local timezone. Values
spread across a collection gap are identified as estimates in the chart.

The hourly view shows the latest seven days, daily shows 90 days, weekly shows
one year, and monthly shows the retained history (two years by default).

## Update locally

```bash
./update_site.sh
```

This fetches one cumulative submission counter from LeetCode, appends it to
`data/twosum_stats.csv`, and generates `public/index.html`.

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup and automation details.

## License

MIT
