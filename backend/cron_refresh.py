#!/usr/bin/env python3
"""
Cron job entry point for refreshing NFL standings data.
This script is designed to be run by Railway's cron service.

It refreshes only the current season's standings and exits cleanly.
"""
import sys
from database import init_db, get_db_session
from models import TeamRealignment
from services.scraper_service import (
    initialize_realignment,
    scrape_current_season,
    REALIGNMENT_DATA
)


def main():
    """Main entry point for cron job - refreshes current season standings."""
    print("=" * 60)
    print("Starting scheduled standings refresh...")
    print("=" * 60)
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Get database session
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
            sys.exit(0)
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Ensure database connection is closed
        db.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()

