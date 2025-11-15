# Quick Start Guide - E-Commerce Fraud Detector

## Prerequisites
- Python 3.13+ installed
- Node.js 18+ installed
- Git (optional)

## Setup & Run (Simple Method)

### Option 1: PowerShell Scripts (Recommended)

1. **Start Backend Server:**
   ```powershell
   .\start-backend.ps1
   ```
   The backend will run on http://localhost:8000

2. **Start Frontend (in a new terminal):**
   ```powershell
   .\start-frontend.ps1
   ```
   The frontend will run on http://localhost:3000 or http://localhost:5173

### Option 2: Manual Setup

#### Backend Setup
```powershell
# Install dependencies
python3 -m pip install --user flask flask-cors flask-limiter sqlalchemy python-dotenv pyjwt joblib scikit-learn pandas numpy nltk

# Run server
cd backend
python3 app.py
```

#### Frontend Setup
```powershell
# Install dependencies
cd frontend-react
npm install

# Start dev server
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:3000 or http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Health Check:** http://localhost:8000/health

## Login Credentials

For testing, use the admin secret from `.env` file:
- **Admin Secret:** `c7883e87ab7e0401ac908fa1f505af3054c763243519e47a579e31c403a151cd`

Or use the default token in the login page hint.

## Testing with TestSprite

### Backend API Tests
```powershell
# Test health endpoint
Invoke-WebRequest http://localhost:8000/health

# Test auth endpoint
$body = @{secret="c7883e87ab7e0401ac908fa1f505af3054c763243519e47a579e31c403a151cd"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/auth/token" -Method POST -Body $body -ContentType "application/json"
```

### Frontend Tests
```powershell
cd frontend-react
npm test
```

## Troubleshooting

### Backend Issues

1. **ModuleNotFoundError: No module named 'flask'**
   - Run: `python3 -m pip install --user -r backend/requirements.txt`

2. **Database Connection Error**
   - The app uses SQLite by default (no database server needed)
   - Database file will be created automatically at `frauddb.db`

3. **Port 8000 already in use**
   - Change `API_PORT` in `.env` file

### Frontend Issues

1. **Cannot find module '@/...'**
   - Restart the dev server: `npm run dev`
   - Clear cache: `npm run build` then `npm run dev`

2. **CORS errors**
   - Ensure backend is running
   - Check `.env` files have correct URLs

3. **Port 3000 already in use**
   - Vite will automatically use port 5173
   - Or specify port: `npm run dev -- --port 3001`

## Features to Test

1. **Login** - Use admin secret to get API token
2. **Dashboard** - View fraud statistics and trends
3. **Predict Review** - Submit a product review for fraud detection
4. **Predict Transaction** - Submit a transaction for fraud analysis
5. **History** - View past predictions

## API Endpoints

- `GET /health` - Health check
- `POST /auth/token` - Get authentication token
- `POST /predict/review` - Predict review fraud
- `POST /predict/transaction` - Predict transaction fraud
- `GET /dashboard/api/stats` - Get fraud statistics
- `GET /dashboard/api/trends` - Get trend data
- `GET /dashboard/api/top-offenders` - Get top offenders
- `GET /dashboard/api/recent-flags` - Get recent flags

## Development Notes

- Models are pre-trained and located in `backend/models/`
- Using SQLite for simplicity (no PostgreSQL setup needed)
- CORS is enabled for local development
- Rate limiting is configured but lenient for development

## Need Help?

Check the main README.md for detailed documentation.
