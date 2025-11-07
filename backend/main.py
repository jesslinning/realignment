from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import traceback
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import init_db, get_db_session
from services.standings_service import get_standings, get_available_seasons

app = FastAPI(title="NFL Standings API")

# Configure CORS - allow requests from frontend
# Get frontend URL from environment variable
frontend_url = os.getenv('FRONTEND_URL', '')
allow_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
allow_credentials = True

# Add production frontend URL if specified
if frontend_url:
    # Remove trailing slash if present (CORS requires exact match)
    frontend_url = frontend_url.rstrip('/')
    # Handle both with and without https://
    if not frontend_url.startswith('http'):
        frontend_url = f"https://{frontend_url}"
    allow_origins.append(frontend_url)
else:
    # If FRONTEND_URL is not set, use wildcard but disable credentials
    # (CORS spec: can't use wildcard with credentials)
    allow_origins = ["*"]
    allow_credentials = False
    print("⚠️ FRONTEND_URL not set - using wildcard CORS (credentials disabled)")

# Print CORS configuration for debugging
print(f"CORS allow_origins: {allow_origins}")
print(f"CORS allow_credentials: {allow_credentials}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler
scheduler = BackgroundScheduler()

def refresh_standings_job():
    """Scheduled job to refresh current season standings."""
    print("=" * 60)
    print("Starting scheduled standings refresh...")
    print("=" * 60)
    
    try:
        from models import TeamRealignment
        from services.scraper_service import (
            initialize_realignment,
            scrape_current_season,
            REALIGNMENT_DATA
        )
        
        db = get_db_session()
        try:
            # Initialize realignment data if needed
            realignment_count = db.query(TeamRealignment).count()
            if realignment_count == 0:
                print("Initializing team realignment data...")
                initialize_realignment(db)
                print(f"✓ Initialized {len(REALIGNMENT_DATA)} teams")
            
            # Scrape current season
            print("Refreshing current season standings...")
            result = scrape_current_season(db)
            
            if result['success']:
                print(f"✓ Successfully refreshed {result['records_updated']} records")
                print(f"  Season: {result['season_scraped']}")
                print("=" * 60)
                print("Refresh completed successfully!")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
        finally:
            db.close()
    except Exception as e:
        print(f"✗ Fatal error in scheduled refresh: {str(e)}")
        import traceback
        traceback.print_exc()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Configure scheduler based on environment variable
    # Default: NFL game schedule - multiple runs on game days
    # Format: "hour minute" (e.g., "3 0" for 3:00 AM) or cron expression
    # For multiple schedules, use comma-separated cron expressions
    refresh_schedule = os.getenv('REFRESH_SCHEDULE', 'nfl_schedule')
    
    if refresh_schedule == 'nfl_schedule':
        # NFL-optimized schedule: Run multiple times on game days
        # Thursday: 4:30 AM UTC (after Thursday Night Football ~11:30 PM ET)
        # Sunday: 9:00 PM, 12:30 AM, 4:30 AM UTC (after early, late, and SNF games)
        # Monday: 4:15 AM UTC (after Monday Night Football ~11:15 PM ET)
        # Other days: 3:00 AM UTC (daily maintenance)
        schedules = [
            ("0 3 * * 0,1,2,5,6", "Daily maintenance"),  # Every day except Thursday (Thu has TNF update)
            ("30 4 * * 4", "After Thursday Night Football"),  # Thursday 4:30 AM UTC
            ("0 21 * * 0", "After Sunday early games"),  # Sunday 9:00 PM UTC (after 1 PM ET games)
            ("30 0 * * 1", "After Sunday late games"),  # Monday 12:30 AM UTC (after 4:25 PM ET games)
            ("30 4 * * 1", "After Sunday Night Football"),  # Monday 4:30 AM UTC (after 8:20 PM ET SNF)
            ("15 4 * * 2", "After Monday Night Football"),  # Tuesday 4:15 AM UTC (after 8:15 PM ET MNF)
        ]
        
        for i, (cron_expr, description) in enumerate(schedules):
            scheduler.add_job(
                refresh_standings_job,
                trigger=CronTrigger.from_crontab(cron_expr),
                id=f'refresh_standings_{i}',
                name=f'Refresh NFL Standings - {description}',
                replace_existing=True
            )
            print(f"Scheduled: {description} - cron: {cron_expr}")
    else:
        # Check if it's a simple "hour minute" format or full cron expression
        if ' ' in refresh_schedule and len(refresh_schedule.split()) == 2:
            # Simple format: "hour minute" -> convert to cron
            hour, minute = refresh_schedule.split()
            cron_expr = f"{minute} {hour} * * *"
            print(f"Scheduling standings refresh with cron: {cron_expr}")
            scheduler.add_job(
                refresh_standings_job,
                trigger=CronTrigger.from_crontab(cron_expr),
                id='refresh_standings',
                name='Refresh NFL Standings',
                replace_existing=True
            )
        else:
            # Assume it's already a cron expression (minute hour day month day_of_week)
            cron_parts = refresh_schedule.split()
            if len(cron_parts) == 5:
                cron_expr = refresh_schedule
                print(f"Scheduling standings refresh with cron: {cron_expr}")
                scheduler.add_job(
                    refresh_standings_job,
                    trigger=CronTrigger.from_crontab(cron_expr),
                    id='refresh_standings',
                    name='Refresh NFL Standings',
                    replace_existing=True
                )
            else:
                # Default fallback
                cron_expr = "0 3 * * *"
                print(f"Invalid schedule format, using default: {cron_expr}")
                scheduler.add_job(
                    refresh_standings_job,
                    trigger=CronTrigger.from_crontab(cron_expr),
                    id='refresh_standings',
                    name='Refresh NFL Standings',
                    replace_existing=True
                )
    
    scheduler.start()
    print("✓ Scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down")

@app.get("/")
async def root():
    return {"message": "NFL Standings API"}

@app.get("/api/standings")
async def standings(season: Optional[int] = None):
    """
    Get NFL standings organized by custom conferences and divisions.
    If season is not provided, uses current season data.
    """
    try:
        return get_standings(season)
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in standings endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching standings: {str(e)}"
        )

@app.get("/api/seasons")
async def seasons():
    """
    Get list of available seasons in the database.
    """
    try:
        seasons_list = get_available_seasons()
        return {"seasons": seasons_list}
    except Exception as e:
        print(f"Error in seasons endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching seasons: {str(e)}"
        )

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/refresh")
async def refresh_standings():
    """
    Manually trigger a standings refresh for the current season.
    Useful for testing or triggering refreshes outside of the cron schedule.
    """
    try:
        from database import get_db_session
        from models import TeamRealignment
        from services.scraper_service import (
            initialize_realignment,
            scrape_current_season,
            REALIGNMENT_DATA
        )
        
        db = get_db_session()
        try:
            # Initialize realignment data if needed
            realignment_count = db.query(TeamRealignment).count()
            if realignment_count == 0:
                initialize_realignment(db)
            
            # Scrape current season
            result = scrape_current_season(db)
            
            if result['success']:
                return {
                    "success": True,
                    "message": "Standings refreshed successfully",
                    "records_updated": result.get('records_updated', 0),
                    "season": result.get('season_scraped')
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Refresh failed: {result.get('error', 'Unknown error')}"
                )
        finally:
            db.close()
    except Exception as e:
        print(f"Error in refresh endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing standings: {str(e)}"
        )

