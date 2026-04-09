# 🏠 Home Command Center

A Skylight Calendar-inspired household chore and task tracker built with Streamlit and SQLite.

## Quick Start

```bash
cd home-command-center
pip install -r requirements.txt
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Features

- **Weekly Calendar View** — See all your chores laid out across the week with color-coded cards
- **Assign to Person** — Color-coded household members with customizable avatars
- **Recurring Tasks** — Set chores to repeat daily, weekly, biweekly, or monthly
- **Categories & Labels** — Group tasks by type (Cleaning, Kitchen, Laundry, etc.) with icons
- **Balance Board** — Blameless equity tracker showing workload distribution, fairness checks, and who-does-what breakdowns
- **Priority Levels** — Low, medium, and high priority with visual indicators
- **Completion Tracking** — Check off tasks and see progress bars in the sidebar

## Default Setup

The app comes pre-loaded with two household members (Justin and Wife — edit names in the sidebar) and 8 common chore categories. Everything is customizable from the Settings panel.

## Data

All data is stored in a local `chores.db` SQLite file created automatically in the app directory. No accounts, no cloud, no subscriptions — you own your data.
