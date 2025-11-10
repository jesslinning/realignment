from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from database import get_db_session
from models import TeamGameScore, TeamRealignment


def get_game_scores(team: str, season: int, db: Optional[Session] = None) -> List[Dict]:
    """
    Get all game scores for a specific team and season.
    
    Args:
        team: Team abbreviation (e.g., 'DAL', 'KC')
        season: Season year (e.g., 2024)
        db: Optional database session. If None, creates a new session.
    
    Returns:
        List of game score dictionaries, ordered by gameday (most recent first).
        Each dictionary includes an 'is_division_game' flag indicating if the opponent
        is in the same division.
    """
    if db is None:
        db = get_db_session()
        close_db = True
    else:
        close_db = False
    
    try:
        # Get the team's division from realignment data
        team_realignment = db.query(TeamRealignment).filter(
            TeamRealignment.team == team.upper()
        ).first()
        
        team_division = team_realignment.division if team_realignment else None
        
        # Create a map of opponent teams to their divisions
        realignments = db.query(TeamRealignment).all()
        opponent_division_map = {
            r.team: r.division
            for r in realignments
        }
        
        # Query game scores for the team and season (most recent first)
        game_scores = db.query(TeamGameScore).filter(
            TeamGameScore.team == team.upper(),
            TeamGameScore.season == season
        ).order_by(TeamGameScore.gameday.desc()).all()
        
        result = []
        for gs in game_scores:
            # Check if opponent is in the same division
            opponent_division = opponent_division_map.get(gs.opponent)
            is_division_game = (
                team_division is not None and
                opponent_division is not None and
                team_division == opponent_division
            )
            
            result.append({
                'id': gs.id,
                'season': gs.season,
                'gameday': gs.gameday.isoformat() if gs.gameday else None,
                'gametime': gs.gametime,
                'score': gs.score,
                'team': gs.team,
                'opponent': gs.opponent,
                'opponent_score': gs.opponent_score,
                'is_win': gs.is_win,
                'is_loss': gs.is_loss,
                'is_tie': gs.is_tie,
                'is_division_game': is_division_game
            })
        
        return result
    finally:
        if close_db:
            db.close()

