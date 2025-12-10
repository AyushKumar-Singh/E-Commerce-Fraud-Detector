# E-Commerce Fraud Detector

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![CI/CD](https://github.com/AyushKumar-Singh/E-Commerce-Fraud-Detector/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AyushKumar-Singh/E-Commerce-Fraud-Detector/actions/workflows/ci-cd.yml)

A production-ready fraud detection system with ML-powered transaction and review analysis.

## 🚀 Quick Links

- [Quick Start Guide](QUICK_START.md) - Get running in minutes
- [Deployment Guide](DEPLOYMENT.md) - Deploy to Vercel, Railway, Docker, or Minikube
- [Testing Guide](TESTING_GUIDE.md) - API and frontend testing
- [CI/CD Pipelines](.github/workflows/) - GitHub Actions workflows

## 📋 Architecture

```
E-Commerce Fraud Detector/
├── backend/              # Python Flask API
│   ├── db/               # SQLAlchemy models & schema
│   ├── models/           # Trained ML models (.pkl)
│   ├── pipelines/        # Feature engineering
│   ├── rules/            # Business rule engine
│   ├── utils/            # Auth, logging, XAI
│   └── app.py            # Main Flask app
│
├── frontend/             # React + TypeScript (Vite)
│   └── src/
│       ├── pages/        # Dashboard, Transactions, Reviews
│       ├── components/   # Reusable UI components
│       └── services/     # API client
│
├── infra/                # Infrastructure configs
│   ├── compose/          # Docker Compose files
│   ├── docker/           # Nginx config
│   └── k8s/              # Kubernetes manifests
│
├── data/                 # Data files
├── monitoring/           # Prometheus config
├── scripts/              # Utility scripts
└── logs/                 # Application logs
```

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL (or use Docker)

### Development Setup

**Backend:**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Run server
python backend/app.py
# API runs at http://localhost:8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
# UI runs at http://localhost:3000
```

### Docker (Recommended)
```powershell
# From project root
docker-compose -f infra/compose/docker-compose.yml up -d

# Services:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Adminer: http://localhost:8080
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/token` | POST | Get API token |
| `/predict/review` | POST | Detect fake reviews |
| `/predict/transaction` | POST | Detect fraud transactions |
| `/predict/transaction-kaggle` | POST | CatBoost fraud detection |
| `/dashboard/*` | GET | Dashboard data |

## 🔄 Data Flow

```mermaid
graph LR
    A[Frontend] --> B[API Gateway]
    B --> C[Feature Engineering]
    C --> D[ML Models]
    D --> E[Business Rules]
    E --> F[Decision Engine]
    F --> G[PostgreSQL]
    F --> H[Response]
```

1. **Request** → Frontend sends transaction/review data
2. **Feature Engineering** → `pipelines/` extracts ML features
3. **ML Prediction** → Trained models score fraud probability
4. **Business Rules** → `rules/` applies domain-specific logic
5. **Decision** → Combined score + explainability returned
6. **Storage** → Results saved to PostgreSQL

## ⚙️ Environment Variables

Copy `.env.production.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/frauddb

# Security (CHANGE THESE!)
JWT_SECRET=your-32-char-secret
ADMIN_SECRET=your-32-char-secret
API_TOKEN=your-32-char-secret

# Model Thresholds
REVIEW_THR=0.65
TX_THR=0.50
```

## 🧪 Testing

```powershell
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guides:
- **Vercel** - Frontend hosting
- **Railway** - Full-stack with managed PostgreSQL
- **Docker** - Self-hosted deployment
- **Minikube** - Local Kubernetes testing

## 🤖 ML Models

| Model | Type | Purpose |
|-------|------|---------|
| Review Model | RandomForest | Fake review detection |
| Transaction Model | IsolationForest | Anomaly-based fraud detection |
| CatBoost Model | CatBoost | Kaggle Credit Card Fraud (99.3% accuracy) |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 E-Commerce Fraud Detector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- [Kaggle Credit Card Fraud Dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud)
- [CatBoost](https://catboost.ai/) for high-performance ML
- [React Query](https://tanstack.com/query) for data fetching
