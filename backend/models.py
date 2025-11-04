from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
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

