from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from database import get_db_session
from models import TeamGameScore


def get_game_scores(team: str, season: int, db: Optional[Session] = None) -> List[Dict]:
    """
    Get all game scores for a specific team and season.
    
    Args:
        team: Team abbreviation (e.g., 'DAL', 'KC')
        season: Season year (e.g., 2024)
        db: Optional database session. If None, creates a new session.
    
    Returns:
        List of game score dictionaries, ordered by gameday (most recent first).
    """
    if db is None:
        db = get_db_session()
        close_db = True
    else:
        close_db = False
    
    try:
        # Query game scores for the team and season (most recent first)
        game_scores = db.query(TeamGameScore).filter(
            TeamGameScore.team == team.upper(),
            TeamGameScore.season == season
        ).order_by(TeamGameScore.gameday.desc()).all()
        
        return [
            {
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
                'is_tie': gs.is_tie
            }
            for gs in game_scores
        ]
    finally:
        if close_db:
            db.close()

