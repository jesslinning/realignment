from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class TeamStanding(Base):
    __tablename__ = 'team_standings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, nullable=False, index=True)
    team = Column(String(3), nullable=False, index=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    win_pct = Column(Float, default=0.0)
    in_division_wins = Column(Integer, default=0)
    in_division_losses = Column(Integer, default=0)
    in_division_ties = Column(Integer, default=0)
    in_division_win_pct = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique season/team combination
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )


class TeamRealignment(Base):
    __tablename__ = 'team_realignment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team = Column(String(3), nullable=False, unique=True, index=True)
    conference = Column(String(50), nullable=False)
    division = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)


class ScrapeLog(Base):
    __tablename__ = 'scrape_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    seasons_scraped = Column(String(255), nullable=False)  # Comma-separated list of seasons
    success = Column(Boolean, default=True)
    error_message = Column(String(1000), nullable=True)
    records_updated = Column(Integer, default=0)


class TeamGameScore(Base):
    __tablename__ = 'team_game_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(Integer, nullable=False, index=True)
    gameday = Column(DateTime, nullable=False, index=True)
    gametime = Column(String(20), nullable=True)  # Game time (e.g., "1:00 PM")
    score = Column(Integer, nullable=False)  # Team's score in this game
    team = Column(String(3), nullable=False, index=True)
    opponent = Column(String(3), nullable=False)  # Opposing team abbreviation
    opponent_score = Column(Integer, nullable=False)  # Opponent's score in this game
    is_win = Column(Integer, default=0)
    is_loss = Column(Integer, default=0)
    is_tie = Column(Integer, default=0)
    
    # Ensure unique season/gameday/team combination
    __table_args__ = (
        UniqueConstraint('season', 'gameday', 'team', name='uq_team_game_score'),
        {'sqlite_autoincrement': True}
    )

