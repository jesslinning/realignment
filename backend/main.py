from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import traceback
from database import init_db
from services.standings_service import get_standings, get_available_seasons

app = FastAPI(title="NFL Standings API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port and CRA default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

