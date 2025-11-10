from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from database import get_db_session
from models import TeamStanding, TeamRealignment


def get_standings_from_db(season: Optional[int] = None, db: Optional[Session] = None) -> list:
    """
    Get standings from database.
    
    Args:
        season: Optional season year. If None, uses most recent season in database.
        db: Optional database session. If None, creates a new session.
    
    Returns:
        List of team standing dictionaries.
    """
    if db is None:
        db = get_db_session()
        close_db = True
    else:
        close_db = False
    
    try:
        query = db.query(TeamStanding)
        
        if season is not None:
            query = query.filter(TeamStanding.season == season)
        else:
            # Get the most recent season
            max_season = db.query(TeamStanding.season).order_by(TeamStanding.season.desc()).first()
            if max_season:
                query = query.filter(TeamStanding.season == max_season[0])
            else:
                return []
        
        standings = query.all()
        
        return [
            {
                'season': s.season,
                'team': s.team,
                'wins': s.wins,
                'losses': s.losses,
                'ties': s.ties,
                'win_pct': s.win_pct,
                'in_division_wins': s.in_division_wins,
                'in_division_losses': s.in_division_losses,
                'in_division_ties': s.in_division_ties,
                'in_division_win_pct': s.in_division_win_pct
            }
            for s in standings
        ]
    finally:
        if close_db:
            db.close()


def get_standings(season: Optional[int] = None, db: Optional[Session] = None) -> Dict:
    """
    Get standings organized by custom conferences and divisions from database.
    
    Args:
        season: Optional season year. If None, uses most recent season in database.
        db: Optional database session. If None, creates a new session.
    
    Returns:
        Dictionary with standings organized by conference and division.
    """
    if db is None:
        db = get_db_session()
        close_db = True
    else:
        close_db = False
    
    try:
        # Get standings from database
        standings_list = get_standings_from_db(season, db)
        
        if not standings_list:
            return {}
        
        # Get realignment data
        realignments = db.query(TeamRealignment).all()
        realignment_map = {
            r.team: {
                'conference': r.conference,
                'division': r.division,
                'name': r.name
            }
            for r in realignments
        }
        
        # Organize by conference and division
        result = {}
        
        # Group standings by conference and division
        for standing in standings_list:
            team = standing['team']
            if team not in realignment_map:
                continue
            
            realignment = realignment_map[team]
            conference = realignment['conference']
            division = realignment['division']
            
            if conference not in result:
                result[conference] = {}
            
            if division not in result[conference]:
                result[conference][division] = []
            
            result[conference][division].append({
                'team': team,
                'name': realignment['name'],
                'wins': standing['wins'],
                'losses': standing['losses'],
                'ties': standing['ties'],
                'win_pct': standing['win_pct'],
                'in_division_wins': standing['in_division_wins'],
                'in_division_losses': standing['in_division_losses'],
                'in_division_ties': standing['in_division_ties'],
                'in_division_win_pct': standing['in_division_win_pct'],
                'season': standing['season']
            })
        
        # Sort teams within each division by win percentage, then by in-division win percentage as tiebreaker
        for conference in result:
            for division in result[conference]:
                result[conference][division].sort(
                    key=lambda x: (x['win_pct'], x['in_division_win_pct']), 
                    reverse=True
                )
        
        return result
    finally:
        if close_db:
            db.close()


def get_available_seasons(db: Optional[Session] = None) -> List[int]:
    """
    Get list of available seasons in the database.
    
    Args:
        db: Optional database session. If None, creates a new session.
    
    Returns:
        List of season years, sorted in descending order.
    """
    if db is None:
        db = get_db_session()
        close_db = True
    else:
        close_db = False
    
    try:
        seasons = db.query(distinct(TeamStanding.season)).order_by(TeamStanding.season.desc()).all()
        return [season[0] for season in seasons]
    finally:
        if close_db:
            db.close()

