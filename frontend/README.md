# NFL Standings Frontend

A React frontend application for displaying NFL standings with custom conference and division realignment.

## Setup

### Prerequisites

- **Node.js** (v18 or higher)
- **npm** (comes with Node.js)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Build

To build for production:
```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

Make sure the backend server is running on `http://localhost:8000` before starting the frontend.

The frontend will automatically fetch standings from the backend API and display them organized by conference and division.

### Local Development

For local development, you don't need to set `VITE_API_URL` because Vite's proxy (configured in `vite.config.js`) automatically forwards `/api/*` requests to the backend.

### Production

In production, you need to set the `VITE_API_URL` environment variable to point to your backend service.

## Environment Variables

### Local Development

Create a `.env` file in the `frontend/` directory (optional):

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000  # Not needed - Vite proxy handles this
```

**Note**: For local development, you don't need to set `VITE_API_URL` because Vite's proxy automatically forwards `/api/*` requests to the backend.

### Production (Railway)

Set `VITE_API_URL` in your Railway frontend service:

**Option 1: Use Public Domain (Recommended)**
```
https://your-backend-service-production-xxxx.up.railway.app
```

**Option 2: Without https:// (code will add it)**
```
your-backend-service-production-xxxx.up.railway.app
```

**Option 3: Using Railway Variable (if supported)**
```
https://${{backend service.RAILWAY_PUBLIC_DOMAIN}}
```

**Important**: 
- Use `RAILWAY_PUBLIC_DOMAIN`, not `RAILWAY_PRIVATE_DOMAIN`
- The variable must be set in the **frontend service**, not backend
- After changing `VITE_API_URL`, you **must rebuild** the frontend (Vite embeds env vars at build time)

## Troubleshooting

### Frontend is Trying to Fetch from Itself

**Symptoms**: Error message "Frontend is trying to fetch from itself" or API calls going to frontend URL instead of backend

**Causes**:
- `VITE_API_URL` is not set
- `VITE_API_URL` is set to an empty string
- `VITE_API_URL` is set to the frontend's own URL
- `VITE_API_URL` is set to a private domain
- Frontend wasn't rebuilt after changing `VITE_API_URL`

**Solutions**:
1. Make sure `VITE_API_URL` is set to your **backend's public domain**
2. Include `https://` or let the code add it automatically
3. Use `RAILWAY_PUBLIC_DOMAIN`, not `RAILWAY_PRIVATE_DOMAIN`
4. **Trigger a rebuild** after changing the variable (Railway should do this automatically, but you can manually redeploy)

### Can't Connect to Backend

**Symptoms**: Network errors, CORS errors, or standings not loading

**Solutions**:
- Make sure backend is running on `http://localhost:8000` (for local dev)
- Use `python -m uvicorn main:app --reload --port 8000` (not just `uvicorn`)
- Check browser console for errors
- Verify Vite proxy is working (check `vite.config.js`)
- For production, verify `VITE_API_URL` is set correctly

### Port 5173 Already in Use

```bash
# Vite will automatically try the next available port
# Or specify a different port:
npm run dev -- --port 5174
```

### Module Not Found Errors

```bash
# Reinstall dependencies
npm install

# Or clear and reinstall
rm -rf node_modules && npm install
```

### Changes Not Reflecting

- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Restart the development server
- Check that Vite's HMR (Hot Module Replacement) is working

### Variable Not Being Read

**Symptoms**: Console shows `VITE_API_URL (raw): (not set)`

**Solutions**:
1. Make sure variable name is exactly `VITE_API_URL` (case-sensitive)
2. Make sure it's set in the **frontend service**, not backend
3. Trigger a rebuild after setting it
4. Check build logs to see if variable is available during build

### Variable Substitution Not Working

**Symptoms**: Using `${{backend service.RAILWAY_PUBLIC_DOMAIN}}` but it's not being replaced

**Solutions**:
1. Hardcode the backend URL instead:
   ```
   https://backend-service-production-xxxx.up.railway.app
   ```
2. Or use Railway's "Reference" feature if available in the UI

## Development Workflow

### Making Changes

1. Edit files in `frontend/src/`
2. Vite's HMR (Hot Module Replacement) updates the page automatically
3. No page refresh needed for most changes

### Testing

You can test the frontend by:
- Opening browser developer tools (F12) → Console tab
- Checking network tab for API calls
- Verifying API calls go to the correct backend URL

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   ├── App.css          # App styles
│   ├── index.css        # Global styles
│   └── components/      # React components
│       ├── StandingsDisplay.jsx
│       ├── ConferenceStandings.jsx
│       └── DivisionStandings.jsx
├── public/              # Static assets
├── package.json         # Node dependencies
└── vite.config.js       # Vite configuration (includes proxy)
```

## Quick Verification Checklist

After deployment:
- [ ] `VITE_API_URL` is set in **frontend service** (not backend)
- [ ] Value is the **backend's public domain** (not frontend's domain)
- [ ] Value includes `https://` or code will add it
- [ ] Frontend service was **redeployed** after setting variable
- [ ] Browser console shows correct `API_URL` value
- [ ] Network tab shows requests going to backend URL (not frontend URL)

## Tips

- **API Documentation**: Backend API docs available at `http://localhost:8000/docs` (when backend is running)
- **Hot Reload**: Vite's HMR updates the page automatically - no refresh needed
- **Console Logs**: Check browser console for API URL and fetch messages
- **Network Tab**: Use browser DevTools Network tab to debug API calls
- **Build Time**: Remember that `VITE_API_URL` is embedded at build time, not runtime
