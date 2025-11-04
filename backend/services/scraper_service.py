import pandas as pd
import numpy as np
import nflreadpy as nfl
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from models import TeamStanding, TeamRealignment, ScrapeLog
from database import get_db_session

# Realignment data - teams organized into custom conferences and divisions
REALIGNMENT_DATA = [
    ['DAL', 'People', 'People with Jobs', 'Cowboys'],
    ['KC', 'People', 'People', 'Chiefs'],
    ['TB', 'People', 'Violent People', 'Buccaneers'],
    ['CIN', 'Animals', 'Cats', 'Bengals'],
    ['MIA', 'Animals', 'Surf & Turf', 'Dolphins'],
    ['CAR', 'Animals', 'Cats', 'Panthers'],
    ['LV', 'People', 'Violent People', 'Raiders'],
    ['ARI', 'Animals', 'North America', 'Cardinals'],
    ['PIT', 'People', 'People with Jobs', 'Steelers'],
    ['NYG', 'People', 'Fictional People', 'Giants'],
    ['TEN', 'People', 'Fictional People', 'Titans'],
    ['SF', 'People', 'People with Jobs', '49ers'],
    ['DET', 'Animals', 'Cats', 'Lions'],
    ['HOU', 'People', 'People', 'Texans'],
    ['BAL', 'Animals', 'Birds of Prey', 'Ravens'],
    ['MIN', 'People', 'Violent People', 'Vikings'],
    ['WAS', 'People', 'People with Jobs', 'Commanders'],
    ['CLE', 'People', 'People', 'Browns'],
    ['JAX', 'Animals', 'Cats', 'Jaguars'],
    ['CHI', 'Animals', 'North America', 'Bears'],
    ['NE', 'People', 'People', 'Patriots'],
    ['BUF', 'Animals', 'Surf & Turf', 'Bills'],
    ['SEA', 'Animals', 'Birds of Prey', 'Seahawks'],
    ['LA', 'Animals', 'Surf & Turf', 'Rams'],
    ['DEN', 'Animals', 'North America', 'Broncos'],
    ['PHI', 'Animals', 'Birds of Prey', 'Eagles'],
    ['ATL', 'Animals', 'Birds of Prey', 'Falcons'],
    ['LAC', 'People', 'Violent People', 'Chargers'],
    ['GB', 'People', 'People with Jobs', 'Packers'],
    ['NYJ', 'People', 'Fictional People', 'Jets'],
    ['IND', 'Animals', 'North America', 'Colts'],
    ['NO', 'People', 'Fictional People', 'Saints']
]


def initialize_realignment(db: Session):
    """Initialize team realignment data in the database."""
    for team_data in REALIGNMENT_DATA:
        team, conference, division, name = team_data
        existing = db.query(TeamRealignment).filter(TeamRealignment.team == team).first()
        if not existing:
            realignment = TeamRealignment(
                team=team,
                conference=conference,
                division=division,
                name=name
            )
            db.add(realignment)
    db.commit()


def calculate_standings_from_scores(scores: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate NFL standings from game scores DataFrame.
    
    Args:
        scores: DataFrame with game data from nflreadpy
    
    Returns:
        DataFrame with standings including wins, losses, ties, and win percentage.
    """
    scores['gameday'] = pd.to_datetime(scores['gameday'])
    
    # Filter to completed regular season games
    today = pd.Timestamp.today()
    scores = scores.loc[
        (scores['gameday'] < f'{today:%Y-%m-%d}')
        & (scores['game_type'] == 'REG')
    ]
    
    if scores.empty:
        return pd.DataFrame(columns=['season', 'team', 'is_win', 'is_loss', 'is_tie', 'pct'])
    
    # Convert to one row per team per game
    long_scores = pd.melt(
        scores, 
        id_vars=['away_team', 'home_team', 'season', 'gameday', 'result'], 
        value_vars=['away_score', 'home_score'], 
        value_name='score'
    )
    long_scores['team'] = long_scores['home_team'].where(
        long_scores['variable'] == 'home_score', 
        long_scores['away_team']
    )
    
    # Determine wins, losses, and ties
    long_scores['is_win'] = 0
    long_scores['is_loss'] = 0
    long_scores['is_tie'] = 0
    
    # Wins: home team wins if result > 0, away team wins if result < 0
    long_scores.loc[
        ((long_scores['variable'] == 'home_score') & (long_scores['result'] > 0)) 
        | ((long_scores['variable'] == 'away_score') & (long_scores['result'] < 0)),
        'is_win'
    ] = 1
    
    # Losses: home team loses if result < 0, away team loses if result > 0
    long_scores.loc[
        ((long_scores['variable'] == 'home_score') & (long_scores['result'] < 0)) 
        | ((long_scores['variable'] == 'away_score') & (long_scores['result'] > 0)),
        'is_loss'
    ] = 1
    
    # Ties: result == 0
    long_scores.loc[long_scores['result'] == 0, 'is_tie'] = 1
    
    long_scores.drop(columns=['away_team', 'home_team'], inplace=True)
    
    # Calculate standings
    standings = long_scores.groupby(['season', 'team'])[['is_win', 'is_loss', 'is_tie']].sum().reset_index()
    standings['pct'] = (standings['is_win'] + standings['is_tie'] / 2) / (
        standings['is_win'] + standings['is_loss'] + standings['is_tie']
    )
    # Replace any NaN values with 0 (for teams with no games)
    standings['pct'] = standings['pct'].fillna(0.0)
    
    return standings


def scrape_season(season: Optional[int], db: Session) -> int:
    """
    Scrape standings for a specific season and store in database.
    
    Args:
        season: Season year. If None, uses current season (seasons=None returns most recent)
        db: Database session
    
    Returns:
        Number of records updated
    """
    try:
        # Load schedule data
        # nflreadpy: seasons=None returns most recent season, seasons=True returns all seasons
        if season is None:
            scores = nfl.load_schedules(seasons=None).to_pandas()  # Most recent season
        else:
            scores = nfl.load_schedules(seasons=season).to_pandas()  # Specific season
        
        # Calculate standings
        standings_df = calculate_standings_from_scores(scores)
        
        if standings_df.empty:
            return 0
        
        records_updated = 0
        for _, row in standings_df.iterrows():
            # Update or create team standing
            existing = db.query(TeamStanding).filter(
                TeamStanding.season == row['season'],
                TeamStanding.team == row['team']
            ).first()
            
            if existing:
                existing.wins = int(row['is_win']) if pd.notna(row['is_win']) else 0
                existing.losses = int(row['is_loss']) if pd.notna(row['is_loss']) else 0
                existing.ties = int(row['is_tie']) if pd.notna(row['is_tie']) else 0
                existing.win_pct = float(row['pct']) if pd.notna(row['pct']) else 0.0
                existing.last_updated = datetime.utcnow()
            else:
                new_standing = TeamStanding(
                    season=int(row['season']),
                    team=row['team'],
                    wins=int(row['is_win']) if pd.notna(row['is_win']) else 0,
                    losses=int(row['is_loss']) if pd.notna(row['is_loss']) else 0,
                    ties=int(row['is_tie']) if pd.notna(row['is_tie']) else 0,
                    win_pct=float(row['pct']) if pd.notna(row['pct']) else 0.0
                )
                db.add(new_standing)
            
            records_updated += 1
        
        db.commit()
        return records_updated
        
    except Exception as e:
        db.rollback()
        raise e


def scrape_all_seasons(db: Session) -> dict:
    """
    Scrape all available seasons and store in database.
    This should be run once for initial setup.
    
    Args:
        db: Database session
    
    Returns:
        Dictionary with scrape results
    """
    try:
        # Load all seasons
        scores = nfl.load_schedules(seasons=True).to_pandas()
        
        # Calculate standings
        standings_df = calculate_standings_from_scores(scores)
        
        if standings_df.empty:
            return {'success': False, 'error': 'No standings data found', 'records_updated': 0}
        
        # Get unique seasons
        seasons = sorted(standings_df['season'].unique())
        seasons_str = ','.join(map(str, seasons))
        
        records_updated = 0
        for _, row in standings_df.iterrows():
            # Update or create team standing
            existing = db.query(TeamStanding).filter(
                TeamStanding.season == row['season'],
                TeamStanding.team == row['team']
            ).first()
            
            if existing:
                existing.wins = int(row['is_win']) if pd.notna(row['is_win']) else 0
                existing.losses = int(row['is_loss']) if pd.notna(row['is_loss']) else 0
                existing.ties = int(row['is_tie']) if pd.notna(row['is_tie']) else 0
                existing.win_pct = float(row['pct']) if pd.notna(row['pct']) else 0.0
                existing.last_updated = datetime.utcnow()
            else:
                new_standing = TeamStanding(
                    season=int(row['season']),
                    team=row['team'],
                    wins=int(row['is_win']) if pd.notna(row['is_win']) else 0,
                    losses=int(row['is_loss']) if pd.notna(row['is_loss']) else 0,
                    ties=int(row['is_tie']) if pd.notna(row['is_tie']) else 0,
                    win_pct=float(row['pct']) if pd.notna(row['pct']) else 0.0
                )
                db.add(new_standing)
            
            records_updated += 1
        
        db.commit()
        
        # Log the scrape
        log = ScrapeLog(
            scrape_date=datetime.utcnow(),
            seasons_scraped=seasons_str,
            success=True,
            records_updated=records_updated
        )
        db.add(log)
        db.commit()
        
        return {
            'success': True,
            'seasons_scraped': seasons_str,
            'records_updated': records_updated
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        # Log the error
        log = ScrapeLog(
            scrape_date=datetime.utcnow(),
            seasons_scraped='',
            success=False,
            error_message=error_msg[:1000],
            records_updated=0
        )
        db.add(log)
        db.commit()
        
        return {
            'success': False,
            'error': error_msg,
            'records_updated': 0
        }


def scrape_current_season(db: Session) -> dict:
    """
    Scrape only the current season and store in database.
    This should be run on a scheduled basis.
    
    Args:
        db: Database session
    
    Returns:
        Dictionary with scrape results
    """
    try:
        records_updated = scrape_season(None, db)  # None = current season
        
        # Get current year for logging
        current_year = datetime.now().year
        seasons_str = str(current_year)
        
        # Log the scrape
        log = ScrapeLog(
            scrape_date=datetime.utcnow(),
            seasons_scraped=seasons_str,
            success=True,
            records_updated=records_updated
        )
        db.add(log)
        db.commit()
        
        return {
            'success': True,
            'season_scraped': current_year,
            'records_updated': records_updated
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        # Log the error
        log = ScrapeLog(
            scrape_date=datetime.utcnow(),
            seasons_scraped='',
            success=False,
            error_message=error_msg[:1000],
            records_updated=0
        )
        db.add(log)
        db.commit()
        
        return {
            'success': False,
            'error': error_msg,
            'records_updated': 0
        }

