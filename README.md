# NFL Standings Application

A full-stack application for displaying NFL standings with custom conference and division realignment.

## Project Structure

```
nfl/
├── backend/          # FastAPI backend service
│   ├── main.py      # API endpoints
│   ├── services/    # Business logic
│   └── requirements.txt
├── frontend/        # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── scratch.py       # Original scratch code (for reference)
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
uvicorn main:app --reload --port 8000
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

## Features

- **Custom Realignment**: Teams are organized into custom conferences (People/Animals) and divisions
- **Standings Display**: Shows wins, losses, ties, and win percentage for each team
- **Season Selection**: View standings for different seasons
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, modern interface with gradient header and styled tables

## API Endpoints

- `GET /api/standings?season=2024` - Get standings for a specific season (season is optional)
- `GET /api/health` - Health check endpoint

## Development

The backend uses FastAPI with automatic API documentation. The frontend uses React with Vite for fast development and hot module replacement.

Both servers support hot reloading during development.

