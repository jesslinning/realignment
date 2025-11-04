# NFL Standings Backend

A FastAPI backend service for NFL standings with custom conference and division realignment.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/standings?season=2024` - Get standings (season is optional, defaults to current season)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

