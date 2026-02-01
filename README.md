# LeetCode Pulse

A monitoring system that tracks real-time solver activity across various LeetCode problem sets. The system aggregates the total number of users currently viewing problems to provide a live "pulse" of activity on the platform.

## 🚀 Live Demo

[View the live dashboard](https://ch2ohch2oh.github.io/leetcodepulse/)

## 📊 Features

- **Real-time Monitoring**: Tracks concurrent users across multiple LeetCode problem sets.
- **Historical Data**: Stores aggregated activity data for trend analysis.
- **Interactive Dashboard**: Visualizes global activity trends over time.
- **Automated Deployment**: GitHub Actions workflow for seamless dashboard updates.

## ⚡ Quick Start

### 1. Update Data
If you have the environment set up, run the update script:
```bash
./update_site.sh
```

### 2. View Dashboard
Open `public/index.html` in your browser or check the live demo.

## 🛠 Development & Setup

For detailed instructions on:
- Setting up the Python virtual environment
- Script usage and command-line flags
- Scheduling automated updates with Cron
- Data file formats

Please refer to [DEVELOPMENT.md](DEVELOPMENT.md).

## License

MIT
