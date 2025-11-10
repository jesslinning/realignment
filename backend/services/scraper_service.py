import pandas as pd
import numpy as np
import nflreadpy as nfl
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from models import TeamStanding, TeamRealignment, ScrapeLog, TeamGameScore
from database import get_db_session

# Realignment data - teams organized into custom conferences and divisions
REALIGNMENT_DATA = [
    ['DAL', 'People', 'People with Jobs', 'Cowboys'],
    ['KC', 'People', 'People', 'Chiefs'],
    ['TB', 'People', 'Violent People', 'Buccaneers'],
    ['CIN', 'Animals', 'Cats', 'Bengals'],
    ['MIA', 'Animals', 'Animals Who Eat Fish', 'Dolphins'],
    ['CAR', 'Animals', 'Cats', 'Panthers'],
    ['LV', 'People', 'Violent People', 'Raiders'],
    ['ARI', 'Animals', "Birds Who Can't Swim", 'Cardinals'],
    ['PIT', 'People', 'People with Jobs', 'Steelers'],
    ['NYG', 'People', 'Fictional People', 'Giants'],
    ['TEN', 'People', 'Fictional People', 'Titans'],
    ['SF', 'People', 'People with Jobs', '49ers'],
    ['DET', 'Animals', 'Cats', 'Lions'],
    ['HOU', 'People', 'People', 'Texans'],
    ['BAL', 'Animals', "Birds Who Can't Swim", 'Ravens'],
    ['MIN', 'People', 'Violent People', 'Vikings'],
    ['WAS', 'People', 'People with Jobs', 'Commanders'],
    ['CLE', 'People', 'People', 'Browns'],
    ['JAX', 'Animals', 'Cats', 'Jaguars'],
    ['CHI', 'Animals', 'Animals Who Eat Fish', 'Bears'],
    ['NE', 'People', 'People', 'Patriots'],
    ['BUF', 'Animals', 'Animals Who Eat Grass', 'Bills'],
    ['SEA', 'Animals', 'Animals Who Eat Fish', 'Seahawks'],
    ['LA', 'Animals', 'Animals Who Eat Grass', 'Rams'],
    ['DEN', 'Animals', 'Animals Who Eat Grass', 'Broncos'],
    ['PHI', 'Animals', 'Animals Who Eat Fish', 'Eagles'],
    ['ATL', 'Animals', "Birds Who Can't Swim", 'Falcons'],
    ['LAC', 'People', 'Violent People', 'Chargers'],
    ['GB', 'People', 'People with Jobs', 'Packers'],
    ['NYJ', 'People', 'Fictional People', 'Jets'],
    ['IND', 'Animals', 'Animals Who Eat Grass', 'Colts'],
    ['NO', 'People', 'Fictional People', 'Saints']
]


def initialize_realignment(db: Session, update_existing: bool = False):
    """
    Initialize team realignment data in the database.
    
    Args:
        db: Database session
        update_existing: If True, updates existing records with new data. 
                        If False (default), only adds new teams.
    """
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
        elif update_existing:
            # Update existing record with new data
            existing.conference = conference
            existing.division = division
            existing.name = name
    db.commit()


def create_game_scores_dataframe(scores: pd.DataFrame) -> pd.DataFrame:
    """
    Transform game scores DataFrame into one row per team per game.
    
    Args:
        scores: DataFrame with game data from nflreadpy
    
    Returns:
        DataFrame with columns: season, gameday, gametime, team, opponent, score, opponent_score, is_win, is_loss, is_tie
    """
    scores['gameday'] = pd.to_datetime(scores['gameday'])
    
    # Filter to completed regular season games
    # A game is considered completed if both home_score and away_score are not null
    # This allows us to include games from today that have finished
    scores = scores.loc[
        (scores['home_score'].notna())
        & (scores['away_score'].notna())
        & (scores['game_type'] == 'REG')
    ]
    
    if scores.empty:
        return pd.DataFrame(columns=['season', 'gameday', 'gametime', 'team', 'opponent', 'score', 'opponent_score', 'is_win', 'is_loss', 'is_tie'])
    
    # Create one row per team per game using the new approach
    sides = [('home', 'away'), ('away', 'home')]
    long_scores = pd.DataFrame()
    
    for side1, side2 in sides:
        side_scores = scores.copy()
        side_scores['team'] = side_scores[f'{side1}_team']
        side_scores['opponent'] = side_scores[f'{side2}_team']
        side_scores['score'] = side_scores[f'{side1}_score']
        side_scores['opponent_score'] = side_scores[f'{side2}_score']
        
        # Determine wins, losses, and ties based on score comparison
        side_scores['is_win'] = (side_scores['score'] > side_scores['opponent_score']).astype(int)
        side_scores['is_loss'] = (side_scores['score'] < side_scores['opponent_score']).astype(int)
        side_scores['is_tie'] = (side_scores['score'] == side_scores['opponent_score']).astype(int)
        
        keep_cols = ['season', 'gameday', 'gametime', 'team', 'opponent', 'score', 'opponent_score', 'is_win', 'is_loss', 'is_tie']
        long_scores = pd.concat([long_scores, side_scores[keep_cols]], ignore_index=True)
    
    # Ensure proper data types
    long_scores['season'] = long_scores['season'].astype(int)
    long_scores['score'] = long_scores['score'].astype(int)
    long_scores['opponent_score'] = long_scores['opponent_score'].astype(int)
    long_scores['is_win'] = long_scores['is_win'].astype(int)
    long_scores['is_loss'] = long_scores['is_loss'].astype(int)
    long_scores['is_tie'] = long_scores['is_tie'].astype(int)
    
    return long_scores


def calculate_standings_from_scores(game_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate NFL standings from game scores DataFrame.
    
    Args:
        game_scores: DataFrame with one row per team per game (from create_game_scores_dataframe)
    
    Returns:
        DataFrame with standings including wins, losses, ties, and win percentage.
    """
    if game_scores.empty:
        return pd.DataFrame(columns=['season', 'team', 'is_win', 'is_loss', 'is_tie', 'pct'])
    
    # Calculate standings
    standings = game_scores.groupby(['season', 'team'])[['is_win', 'is_loss', 'is_tie']].sum().reset_index()
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
        
        # Create game scores dataframe
        game_scores_df = create_game_scores_dataframe(scores)
        
        if game_scores_df.empty:
            return 0
        
        # Save game scores to database
        game_scores_updated = 0
        for _, row in game_scores_df.iterrows():
            # Check if this game score already exists
            existing = db.query(TeamGameScore).filter(
                TeamGameScore.season == int(row['season']),
                TeamGameScore.gameday == row['gameday'],
                TeamGameScore.team == row['team']
            ).first()
            
            if existing:
                # Update existing record
                existing.gametime = row['gametime'] if pd.notna(row['gametime']) else None
                existing.score = int(row['score'])
                existing.opponent = row['opponent']
                existing.opponent_score = int(row['opponent_score'])
                existing.is_win = int(row['is_win'])
                existing.is_loss = int(row['is_loss'])
                existing.is_tie = int(row['is_tie'])
            else:
                # Create new record
                new_game_score = TeamGameScore(
                    season=int(row['season']),
                    gameday=row['gameday'],
                    gametime=row['gametime'] if pd.notna(row['gametime']) else None,
                    score=int(row['score']),
                    team=row['team'],
                    opponent=row['opponent'],
                    opponent_score=int(row['opponent_score']),
                    is_win=int(row['is_win']),
                    is_loss=int(row['is_loss']),
                    is_tie=int(row['is_tie'])
                )
                db.add(new_game_score)
            
            game_scores_updated += 1
        
        # Calculate standings from game scores
        standings_df = calculate_standings_from_scores(game_scores_df)
        
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
        
        # Create game scores dataframe
        game_scores_df = create_game_scores_dataframe(scores)
        
        if game_scores_df.empty:
            return {'success': False, 'error': 'No game scores data found', 'records_updated': 0}
        
        # Get unique seasons from game scores
        seasons = sorted(game_scores_df['season'].unique())
        seasons_str = ','.join(map(str, seasons))
        
        # Save game scores to database
        game_scores_updated = 0
        for _, row in game_scores_df.iterrows():
            # Check if this game score already exists
            existing = db.query(TeamGameScore).filter(
                TeamGameScore.season == int(row['season']),
                TeamGameScore.gameday == row['gameday'],
                TeamGameScore.team == row['team']
            ).first()
            
            if existing:
                # Update existing record
                existing.gametime = row['gametime'] if pd.notna(row['gametime']) else None
                existing.score = int(row['score'])
                existing.opponent = row['opponent']
                existing.opponent_score = int(row['opponent_score'])
                existing.is_win = int(row['is_win'])
                existing.is_loss = int(row['is_loss'])
                existing.is_tie = int(row['is_tie'])
            else:
                # Create new record
                new_game_score = TeamGameScore(
                    season=int(row['season']),
                    gameday=row['gameday'],
                    gametime=row['gametime'] if pd.notna(row['gametime']) else None,
                    score=int(row['score']),
                    team=row['team'],
                    opponent=row['opponent'],
                    opponent_score=int(row['opponent_score']),
                    is_win=int(row['is_win']),
                    is_loss=int(row['is_loss']),
                    is_tie=int(row['is_tie'])
                )
                db.add(new_game_score)
            
            game_scores_updated += 1
        
        # Calculate standings from game scores
        standings_df = calculate_standings_from_scores(game_scores_df)
        
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

