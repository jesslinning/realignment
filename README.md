# NFL Standings Application

A full-stack application for displaying NFL standings with custom conference and division realignment.

## Features

- **Custom Realignment**: Teams are organized into custom conferences (People/Animals) and divisions
- **Standings Display**: Shows wins, losses, ties, and win percentage for each team
- **Season Selection**: View standings for different seasons
- **Game Scores**: View detailed game scores with division game indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, modern interface with gradient header and styled tables
- **Automatic Updates**: Scheduled database refreshes using APScheduler

## Project Structure

```
realignment/
├── backend/          # FastAPI backend service
│   ├── main.py      # API endpoints
│   ├── database.py  # Database configuration
│   ├── models.py   # SQLAlchemy models
│   ├── scrape.py    # Scraper script
│   ├── services/    # Business logic
│   └── requirements.txt
├── frontend/        # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── README.md
```

## Quick Start

### Prerequisites

- **Python 3.10 or higher** (3.12 recommended)
- **Node.js** (v18 or higher)
- **npm** (comes with Node.js)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start the backend server first (port 8000)
2. Start the frontend development server (port 5173)
3. Open your browser to `http://localhost:5173`
4. The standings will automatically load for the current season
5. You can change the season using the season selector in the header

## Initial Database Setup

The first time you run the backend, you'll need to populate the database:

### Option 1: Use the Scraper Script

```bash
# Make sure backend virtual environment is activated
cd backend

# Scrape all seasons (takes a few minutes)
python scrape.py --all

# Or just scrape current season (faster)
python scrape.py
```

### Option 2: Use the API Endpoint

After starting the backend, you can trigger a refresh via the API:

```bash
curl -X POST http://localhost:8000/api/refresh
```

## API Endpoints

- `GET /api/standings?season=2024` - Get standings for a specific season (season is optional)
- `GET /api/seasons` - Get list of available seasons
- `GET /api/game-scores?team=DAL&season=2024` - Get game scores for a team
- `GET /api/health` - Health check endpoint
- `POST /api/refresh` - Manually trigger a standings refresh

## Development

The backend uses FastAPI with automatic API documentation. The frontend uses React with Vite for fast development and hot module replacement.

Both servers support hot reloading during development.

## Documentation

For more detailed information, see:
- [Backend README](backend/README.md) - Backend setup, deployment, and troubleshooting
- [Frontend README](frontend/README.md) - Frontend setup and configuration

## Deployment

This application can be deployed to Railway or similar platforms. See the backend README for detailed deployment instructions.
