# Quick Start Guide - E-Commerce Fraud Detector

Get the application running in minutes!

## Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- PostgreSQL (or Docker for containerized setup)

---

## Option 1: Docker (Recommended)

The fastest way to get everything running:

```powershell
# Start all services with Docker Compose
docker-compose -f infra/compose/docker-compose.yml up -d

# Verify services are running
docker-compose -f infra/compose/docker-compose.yml ps
```

**Access points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Adminer (DB Admin): http://localhost:8080

---

## Option 2: Manual Setup

### Step 1: Backend Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Start the backend server
python backend/app.py
```

Backend will run at: http://localhost:8000

### Step 2: Frontend Setup

Open a **new terminal**:

```powershell
cd frontend
npm install
npm run dev
```

Frontend will run at: http://localhost:3000 or http://localhost:5173

---

## Accessing the Application

1. Open http://localhost:3000 in your browser
2. The dashboard should load showing fraud statistics
3. Use the API token `vUfIt9RDa2BLiYEcmwSp5VoCkNlQMgbT` (from `.env`)

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/token` | POST | Get authentication token |
| `/predict/review` | POST | Analyze review for fraud |
| `/predict/transaction` | POST | Analyze transaction for fraud |
| `/dashboard/api/*` | GET | Dashboard data |

### Test the API:

```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# Predict a review (requires API token)
$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "vUfIt9RDa2BLiYEcmwSp5VoCkNlQMgbT" }
$body = '{"user_id": 1, "product_id": "TEST", "review_text": "Great product!", "rating": 5}'
Invoke-RestMethod -Uri "http://localhost:8000/predict/review" -Method Post -Headers $headers -Body $body
```

---

## Features to Test

1. **Dashboard** - View real-time fraud statistics
2. **Review Analysis** - Submit reviews for fake detection
3. **Transaction Analysis** - Submit transactions for fraud detection
4. **Model Metrics** - View ML model performance

---

## Troubleshooting

### Backend Issues

| Problem | Solution |
|---------|----------|
| Port 8000 in use | Change `API_PORT` in `.env` |
| Database connection error | Check PostgreSQL is running |
| Module not found | Run `pip install -r backend/requirements.txt` |

### Frontend Issues

| Problem | Solution |
|---------|----------|
| Port 3000/5173 in use | Use `npm run dev -- --port 3001` |
| CORS errors | Ensure backend is running on port 8000 |
| Build errors | Delete `node_modules` and run `npm install` |

---

## Next Steps

- See [DEPLOYMENT.md](DEPLOYMENT.md) for deploying to Vercel, Railway, Docker, or Minikube
- See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions
- Check [Readme.md](Readme.md) for full project documentation

---

## Development Notes

- ML models are pre-trained in `backend/models/`
- Rate limiting is configured but lenient for development
- CORS is enabled for localhost development
