# NFL Standings Scraper

This scraper fetches NFL standings data from nflreadpy and stores it in a SQLite database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database (run once):
```bash
python scrape.py --all
```

This will:
- Create the database and tables
- Initialize team realignment data
- Scrape all available seasons from nflreadpy

## Usage

### Initial Setup (All Seasons)
Run this once to populate the database with historical data:
```bash
python scrape.py --all
```

### Scheduled Scraping (Current Season Only)
For regular updates, run without arguments to scrape only the current season:
```bash
python scrape.py
```

This is what you should run on a schedule (e.g., daily or weekly).

### Scrape Specific Season
To update a specific season:
```bash
python scrape.py --season 2023
```

## Scheduling

### Using Cron (Linux/Mac)
Add to your crontab (`crontab -e`):
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/nfl/backend && /path/to/python scrape.py

# Or weekly on Mondays at 2 AM
0 2 * * 1 cd /path/to/nfl/backend && /path/to/python scrape.py
```

### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly)
4. Action: Start a program
5. Program: `python`
6. Arguments: `scrape.py`
7. Start in: `C:\path\to\nfl\backend`

### Using systemd (Linux)
Create `/etc/systemd/system/nfl-scraper.service`:
```ini
[Unit]
Description=NFL Standings Scraper
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/nfl/backend
ExecStart=/path/to/python scrape.py

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/nfl-scraper.timer`:
```ini
[Unit]
Description=Daily NFL Standings Scraper

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable nfl-scraper.timer
sudo systemctl start nfl-scraper.timer
```

## Database Location

By default, the database is stored at:
- `./nfl_standings.db` (relative to where you run the script)

You can change this by setting the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="sqlite:///./nfl_standings.db"
```

## Database Schema

- **team_standings**: Stores wins, losses, ties, and win percentage for each team/season
- **team_realignment**: Stores custom conference and division assignments
- **scrape_logs**: Tracks scraping history and errors

## Notes

- The scraper automatically updates existing records for the same season/team combination
- Failed scrapes are logged in the `scrape_logs` table
- The first scrape (--all) may take several minutes as it processes all historical seasons
- Subsequent scrapes (current season only) are much faster

