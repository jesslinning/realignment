#!/usr/bin/env python3
"""
Scraper script for NFL standings data.

Usage:
    # Initial scrape (all seasons)
    python scrape.py --all
    
    # Scrape current season only
    python scrape.py
    
    # Scrape specific season
    python scrape.py --season 2023
"""
import argparse
import sys
from database import init_db, get_db_session
from models import TeamRealignment
from services.scraper_service import (
    initialize_realignment,
    scrape_all_seasons,
    scrape_current_season,
    scrape_season,
    REALIGNMENT_DATA
)


def main():
    parser = argparse.ArgumentParser(description='Scrape NFL standings data')
    parser.add_argument('--all', action='store_true', help='Scrape all seasons (initial setup)')
    parser.add_argument('--season', type=int, help='Scrape specific season')
    args = parser.parse_args()
    
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
        
        if args.all:
            print("Scraping all seasons (this may take a while)...")
            result = scrape_all_seasons(db)
            if result['success']:
                print(f"✓ Successfully scraped {result['records_updated']} records")
                print(f"  Seasons: {result['seasons_scraped']}")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        elif args.season:
            print(f"Scraping season {args.season}...")
            records_updated = scrape_season(args.season, db)
            print(f"✓ Successfully scraped {records_updated} records for season {args.season}")
        else:
            print("Scraping current season...")
            result = scrape_current_season(db)
            if result['success']:
                print(f"✓ Successfully scraped {result['records_updated']} records")
                print(f"  Season: {result['season_scraped']}")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
                sys.exit(1)
    
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()

