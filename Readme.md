<<<<<<< HEAD
# E-Commerce Fraud Detector

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![CI/CD](https://github.com/AyushKumar-Singh/E-Commerce-Fraud-Detector/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AyushKumar-Singh/E-Commerce-Fraud-Detector/actions/workflows/ci-cd.yml)

A production-ready fraud detection system with ML-powered transaction and review analysis.
=======
# 🚨 E-Commerce Fraud Detector  
### **AI-Powered Fraud & Fake Review Detection System**

A full-stack, production-ready fraud detection platform combining **NLP**, **anomaly detection**, **behavioral analytics**, and a secure **Flask + PostgreSQL backend**.  
Designed to help e-commerce platforms detect and prevent fraudulent activities in real time.

---

## ⭐ Overview  
The **E-Commerce Fraud Detector** is a dual-module AI system built to identify:

- Fraudulent or suspicious e-commerce transactions  
- Fake, manipulated, or bot-generated product reviews  
- Abnormal behavioral patterns such as velocity spikes or device/IP anomalies  

The project integrates **ML models**, **real-time APIs**, **security layers**, and **scalable deployment** using Docker.

---

## 🎯 Objectives  
- Detect fake reviews using NLP-based sentiment and authenticity scoring  
- Identify abnormal transactions using Isolation Forest  
- Analyze user patterns, IP/device fingerprints, and spending behavior  
- Provide secure, real-time fraud prediction via Flask API  
- Create explainable fraud insights for business decision-making  
- Deploy as a scalable microservice architecture using Docker  

---

## 🔥 Unique Features

### 🧠 **Dual AI Modules**
#### **1. Fake Review Detector**
- NLP preprocessing (tokenization, stopwords, lemmatization)  
- Sentiment analysis  
- Logistic Regression classifier  
- Text authenticity heuristics  

#### **2. Transaction Fraud Detector**
- Isolation Forest anomaly detection  
- Statistical feature extraction  
- Velocity checks & behavioral flags  
- IP/device fingerprint consistency  

---

### 🛡️ Security & Reliability
- JWT-based authentication  
- Hybrid AI + rule-based verification  
- Device/IP fingerprinting  
- Confidence scores via XAI  
- Rate limiting & request validation  

---

### 📊 Behavioral Analytics
- Spending spike detection  
- Review frequency patterns  
- User trust scoring  
- Admin-level fraud insights dashboard (optional React app)

---

## ⚠️ Risks & Mitigation

| Risk Type | Description | Mitigation |
|----------|-------------|------------|
| False Positives | Legit users mistakenly flagged | Threshold tuning, XAI scoring |
| Evasion Attempts | Fraudsters modify patterns | Hybrid rules, pattern randomization |
| Data Drift | Behavior changes over time | Retraining pipelines |
| Automated Bots | Manipulated reviews | NLP classifiers + spam detection |
| Misinformation | Fake textual patterns | Review authenticity features |

---

## 🏗️ Tech Stack

### **Backend**
- Python  
- Flask  
- scikit-learn  
- NLTK  
- SQLAlchemy  

### **Database**
- PostgreSQL  

### **Deployment**
- Docker / Docker Compose  
- REST API endpoints  
- Token authentication  

### **Frontend (Optional Dashboard)**
- React  
- TypeScript  
- Vite  
- Tailwind CSS  
- Fraud insights data visualization  

---

## 🧠 Machine Learning Models

| Module | Model | Purpose |
|--------|--------|---------|
| Fake Review Detector | Logistic Regression | Detect fake/manipulated reviews |
| Fraud Transaction Detector | Isolation Forest | Identify abnormal spending patterns |

---

## 📊 Key Analytical Features
- Sentiment scoring  
- Review authenticity heuristics  
- Transaction velocity & spikes  
- User trust score  
- Device/IP risk scoring  
- Multi-metric fraud score  

---

## 🚀 Installation & Setup

### **Clone the repository**
```bash
git clone https://github.com/yourusername/E-Commerce-Fraud-Detector.git
cd E-Commerce-Fraud-Detector
```

---

## 🔧 Backend Setup (Flask API)
```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/frauddb
SECRET_KEY=your_secret_key
```

Run development server:
```bash
python app.py
```
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3

## 🚀 Quick Links

<<<<<<< HEAD
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
=======
## 🎨 Frontend Setup (Optional React Dashboard)

```bash
cd frontend
npm install
npm run dev
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3
```

## ⚡ Quick Start

<<<<<<< HEAD
### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL (or use Docker)

### Development Setup
=======
## 🐳 Docker Deployment

```bash
docker compose up --build
```

Stop:
```bash
docker compose down
```
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3

**Backend:**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

<<<<<<< HEAD
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
=======
## 📡 API Endpoints

### **POST /predict/review**
Input:
```json
{
  "review_text": "The product was amazing!"
}
```

### **POST /predict/transaction**
Input:
```json
{
  "amount": 2500,
  "ip": "192.168.0.12",
  "device": "mobile",
  "frequency": 12
}
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3
```

## 🔌 API Endpoints

<<<<<<< HEAD
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
=======
## 🧪 Testing

```bash
pytest
```
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3

# Model Thresholds
REVIEW_THR=0.65
TX_THR=0.50
```

<<<<<<< HEAD
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
=======
## 🧭 Future Enhancements
- BERT/LSTM for more accurate review authenticity detection  
- Blockchain verification for transaction integrity  
- Advanced fraud dashboard with alerts  
- SaaS multi-tenant architecture  
- Online learning pipeline for continuous training  
- Image-based fake product detection  
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3

```
MIT License

<<<<<<< HEAD
Copyright (c) 2025 E-Commerce Fraud Detector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
=======
## 🤝 Contributing  
Pull requests are welcome — ensure that tests pass and code is formatted properly.
>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

<<<<<<< HEAD
## 🙏 Acknowledgments

- [Kaggle Credit Card Fraud Dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud)
- [CatBoost](https://catboost.ai/) for high-performance ML
- [React Query](https://tanstack.com/query) for data fetching
=======
## 👤 Author  
**Ayush Kumar Singh**  
AI Systems Architect & LLM Infrastructure Engineer  
LinkedIn: ayush-kumar-singh  
GitHub: AyushKumar-Singh

>>>>>>> 6aa39faa21e892b26da17db0e90da00c895330a3
