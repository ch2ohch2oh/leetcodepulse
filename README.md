# Two Sum Pulse

A tiny activity monitor for LeetCode. It uses the number of new submissions to
[Two Sum](https://leetcode.com/problems/two-sum/) as a simple, recognizable pulse
of coding activity.

## Live dashboard

[View Two Sum Pulse](https://ch2ohch2oh.github.io/leetcodepulse/)

The dashboard shows new Two Sum submissions over a rolling hour, day, week, or
month and charts the historical rate for the selected interval.

## Update locally

```bash
./update_site.sh
```

This fetches one cumulative submission counter from LeetCode, appends it to
`data/twosum_stats.csv`, and generates `public/index.html`.

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup and automation details.

## License

MIT
