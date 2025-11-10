# NFL Standings Backend

A FastAPI backend service for NFL standings with custom conference and division realignment.

## Setup

### Prerequisites

- **Python 3.10 or higher** (3.12 recommended to match production)
- **Important**: `nflreadpy` requires Python >= 3.10

### Installation

1. Create a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Upgrade pip:
```bash
pip install --upgrade pip
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python -m uvicorn main:app --reload --port 8000
```

**Important**: Always use `python -m uvicorn` instead of just `uvicorn` to ensure you're using the venv's Python, not system/Anaconda Python.

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/standings?season=2024` - Get standings (season is optional, defaults to current season)
- `GET /api/seasons` - Get list of available seasons
- `GET /api/game-scores?team=DAL&season=2024` - Get game scores for a team
- `POST /api/refresh` - Manually trigger a standings refresh

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Setup

### Initial Population

The first time you run the backend, populate the database:

```bash
# Scrape all seasons (takes a few minutes)
python scrape.py --all

# Or just scrape current season (faster)
python scrape.py
```

### Database Location

- **Local Development**: Uses SQLite by default (`nfl_standings.db` in backend directory)
- **Production**: Uses PostgreSQL (configured via `DATABASE_URL` environment variable)

### Database Schema

- **team_standings**: Stores wins, losses, ties, and win percentage for each team/season
- **team_realignment**: Stores custom conference and division assignments
- **game_scores**: Stores individual game results
- **scrape_logs**: Tracks scraping history and errors

## Scraper

The scraper fetches NFL standings data from `nflreadpy` and stores it in the database.

### Usage

```bash
# Initial scrape (all seasons)
python scrape.py --all

# Scrape current season only (for regular updates)
python scrape.py

# Scrape specific season
python scrape.py --season 2023
```

### Manual Refresh

You can trigger a manual refresh using the API endpoint:

```bash
curl -X POST http://localhost:8000/api/refresh
```

## Scheduled Refreshes (APScheduler)

The backend includes APScheduler for automatic database refreshes. The scheduler runs in the background within the FastAPI service.

### Default Schedule

By default, the refresh runs on an NFL-optimized schedule:
- **Thursday 4:30 AM UTC**: After Thursday Night Football
- **Sunday 9:00 PM UTC**: After early afternoon games
- **Monday 12:30 AM UTC**: After late afternoon games
- **Monday 4:30 AM UTC**: After Sunday Night Football
- **Tuesday 4:15 AM UTC**: After Monday Night Football
- **Daily 3:00 AM UTC**: Maintenance update (all other days)

### Custom Schedule

To customize the schedule, set the `REFRESH_SCHEDULE` environment variable:

**Simple Format:**
```
REFRESH_SCHEDULE="3 0"  # 3:00 AM UTC daily
```

**Cron Format:**
```
REFRESH_SCHEDULE="0 3 * * *"  # 3:00 AM UTC daily
REFRESH_SCHEDULE="0 */6 * * *"  # Every 6 hours
REFRESH_SCHEDULE="0 3,15 * * *"  # 3:00 AM and 3:00 PM UTC daily
```

**NFL-Optimized Schedule:**
```
REFRESH_SCHEDULE=nfl_schedule  # Uses the default NFL-optimized schedule
```

### Monitoring

Check the logs to see scheduler activity:
- When it starts: `"✓ Scheduler started"`
- When jobs run: `"Starting scheduled standings refresh..."`
- Job results: `"✓ Successfully refreshed X records"` or error messages

## Environment Variables

### Local Development

Create a `.env` file in the `backend/` directory (optional):

```bash
DATABASE_URL=sqlite:///./nfl_standings.db  # Default, can omit
FRONTEND_URL=http://localhost:5173          # Default, can omit
REFRESH_SCHEDULE=nfl_schedule                # Default, can omit
```

### Production (Railway)

Required variables:
- `DATABASE_URL` - PostgreSQL connection string (automatically provided by Railway PostgreSQL service)

Optional variables:
- `FRONTEND_URL` - Frontend URL for CORS (e.g., `https://your-frontend.up.railway.app`)
- `REFRESH_SCHEDULE` - Custom refresh schedule (defaults to NFL-optimized schedule)

## Deployment to Railway

### Pre-Deployment Checklist

- ✅ All code changes are committed and pushed
- ✅ Database migration scripts exist (if needed)
- ✅ Environment variables are configured

### Deployment Steps

1. Push your changes:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Railway will automatically detect the push and start a new deployment.

2. Monitor the deployment:
   - Go to your Railway project dashboard
   - Click on your **backend service**
   - Go to the **Deployments** tab
   - Watch the deployment logs

3. Configure environment variables:
   - Go to **Variables** tab
   - Set `DATABASE_URL` (usually auto-provided by Railway PostgreSQL)
   - Set `FRONTEND_URL` (optional, for CORS)
   - Set `REFRESH_SCHEDULE` (optional, defaults to NFL schedule)

4. Verify deployment:
   - Check health endpoint: `https://your-backend.up.railway.app/api/health`
   - Check API docs: `https://your-backend.up.railway.app/docs`
   - Trigger a manual refresh: `POST /api/refresh`

### Database Migrations

Migrations run automatically on startup. The `init_db()` function checks and adds missing columns automatically.

If you need to run migrations manually:

```bash
# Using Railway CLI
railway run python migrate_add_in_division_standings.py

# Or via Railway web console
# Go to Deployments → Latest → Run Command
```

## Troubleshooting

### ModuleNotFoundError (e.g., "No module named 'apscheduler'")

This usually means uvicorn is using the wrong Python (e.g., Anaconda).

**Solution:**
```bash
# Always use 'python -m uvicorn' instead of just 'uvicorn'
python -m uvicorn main:app --reload --port 8000

# Or deactivate Anaconda first:
conda deactivate
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### nflreadpy Installation Fails

**Check Python version:**
```bash
python --version  # Should be 3.10.x, 3.11.x, 3.12.x, or 3.13.x
```

**Solutions:**
1. Upgrade pip:
```bash
pip install --upgrade pip setuptools wheel
```

2. Clear pip cache:
```bash
pip cache purge
pip install nflreadpy
```

3. Install dependencies separately:
```bash
pip install pandas numpy pyarrow
pip install nflreadpy
```

4. Use uv (recommended by nflreadpy):
```bash
pip install uv
uv pip install -r requirements.txt
```

5. If using Python 3.13, there might be compatibility issues - use Python 3.12 instead

### Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000  # macOS/Linux

# Use a different port:
python -m uvicorn main:app --reload --port 8001
```

### Database Errors

- Make sure you've run the scraper at least once: `python scrape.py`
- Check that `nfl_standings.db` exists in the `backend/` directory (for SQLite)
- Verify `DATABASE_URL` is set correctly (for PostgreSQL)

### Scheduler Not Starting

**Symptoms**: No "Scheduler started" message in logs

**Solutions:**
- Check that `apscheduler==3.10.4` is in `requirements.txt`
- Check Railway logs for import errors
- Ensure the service deployed successfully

### Refresh Not Running

**Symptoms**: No refresh messages at scheduled time

**Solutions:**
1. Check the cron expression is valid
2. Verify the schedule is in UTC
3. Check logs for error messages
4. Try triggering manually with `/api/refresh` to test the refresh function

## Local Development Tips

- **Always use `python -m uvicorn`**: This ensures you're using the venv's Python
- **Python Version**: Make sure you're using Python 3.10+ (3.12 recommended)
- **API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs
- **Hot Reload**: Server auto-reloads with `--reload` flag
- **Database**: Use `python scrape.py` to refresh standings data locally
- **Scheduler**: Runs in background but won't cause issues - just logs to console

## Project Structure

```
backend/
├── main.py              # FastAPI app and API endpoints
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── scrape.py            # Scraper script
├── requirements.txt     # Python dependencies
├── services/
│   ├── scraper_service.py
│   ├── standings_service.py
│   └── game_scores_service.py
└── nfl_standings.db     # SQLite database (created on first run)
```
