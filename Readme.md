# 🛡️ E-Commerce Fraud Detector

[![CI/CD](https://github.com/yourusername/fraud-detector/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/fraud-detector/actions)
[![codecov](https://codecov.io/gh/yourusername/fraud-detector/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/fraud-detector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> AI-Powered Fraud and Fake Review Detection System for modern e-commerce platforms.  
> Protect your marketplace from fraudulent transactions and manipulative reviews using state-of-the-art machine learning, real-time behavioral analysis, and explainable AI.

---

## 🌟 Features

### Dual Detection System
- 🔍 Fake Review Detection — NLP sentiment analysis using Logistic Regression
- 💳 Transaction Fraud Detection — Anomaly detection via Isolation Forest

### Advanced Analytics
- Behavioral Pattern Analysis — IP, user, and device fingerprinting
- Velocity Monitoring — Detect spending spikes and review bursts
- Explainable AI — Confidence scores and human-readable reasoning

### Production-Ready
- REST API (Flask) — Real-time prediction endpoints
- Dockerized & Scalable — PostgreSQL + Docker + Redis
- Security — Token/JWT authentication, rate limiting, and secure API calls
- Monitoring — Prometheus + Grafana metrics and structured logging

---

## 📊 Architecture

```text
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│  Client     │──▶│    NGINX     │──▶│   Flask API │
│ (Frontend)  │   │ (Reverse     │   │ (Gunicorn)  │
└─────────────┘   │   Proxy)     │   └──────┬──────┘
                  └──────────────┘          │
                                            ▼
            ┌────────────────────────────────────────┐
            │      Backend Infrastructure             │
            │ ┌──────────────┬──────────────┬───────┐ │
            │ │ PostgreSQL   │ Redis Cache  │ Models│ │
            │ │ Transactions │ Sessions     │  ML   │ │
            │ └──────────────┴──────────────┴───────┘ │
            └────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+
- Git

### Installation

```bash
# 1️⃣ Clone repository
git clone https://github.com/yourusername/fraud-detector.git
cd fraud-detector

# 2️⃣ Setup environment
cp .env.example .env
# Edit .env with your configuration

# 3️⃣ Install dependencies
make install

# 4️⃣ Initialize database
make db-init

# 5️⃣ Start services
make docker-up
```

### Verify Installation

```bash
# Check API health
curl http://localhost:8000/health
```

Access points:
- API: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard
- Adminer (DB UI): http://localhost:8080
- Grafana: http://localhost:3000

---

## 📡 API Usage

### Authentication
All endpoints require API key or JWT:

```bash
# Using API Key
curl -H "X-API-Key: your_api_token" http://localhost:8000/predict/review
```

### Predict Fake Review

POST /predict/review

Request:
```json
{
  "user_id": 123,
  "product_id": "PROD-456",
  "review_text": "Amazing product!!! BEST EVER!!!",
  "rating": 5,
  "ip_address": "192.168.1.1",
  "device_fingerprint": "abc123xyz"
}
```

Response:
```json
{
  "review_id": 789,
  "decision": true,
  "confidence": "high",
  "score_model": 0.8234,
  "score_rules": 0.15,
  "score_final": 0.9734,
  "threshold": 0.65,
  "reasons": [
    "⚠️ Excessive uppercase usage",
    "⚠️ IP review burst (50+ reviews in 30 days)"
  ],
  "model_contribution": 84.6,
  "rules_contribution": 15.4
}
```

### Predict Fraudulent Transaction

POST /predict/transaction

Request:
```json
{
  "user_id": 123,
  "amount": 50000.00,
  "currency": "INR",
  "channel": "web",
  "ip_address": "192.168.1.1",
  "device_fingerprint": "xyz789"
}
```

Response:
```json
{
  "transaction_id": 456,
  "decision": true,
  "confidence": "high",
  "score_final": 0.89,
  "reasons": [
    "⚠️ High-value transaction (>50,000)",
    "⚠️ Transaction from unusual location"
  ]
}
```

---

## 🧠 Machine Learning Pipeline

### Review Features (25+)
- Text: TF-IDF, punctuation, uppercase ratio
- Behavioral: Account age, review frequency, deviation from average rating
- Network: Device/IP velocity and clustering patterns

### Transaction Features (20+)
- Amount: Z-scores, rolling mean/std deviation
- Velocity: Transactions per time window
- Context: Channel, geo-location, and mismatch checks

Task / Model / Performance:
- Fake Reviews: Logistic Regression + TF-IDF — ROC-AUC: 0.94
- Fraudulent Transactions: Isolation Forest — ROC-AUC: 0.89

---

## 🧪 Testing

```bash
# Unit tests
make test

# Integration tests
make test-integration

# Load testing
make load-test

# Coverage report
pytest --cov=backend --cov-report=html
```

---

## 📊 Dashboard Features

- Real-time fraud trends and daily statistics
- Flagged users, IPs, and devices
- Admin feedback (human-in-the-loop labeling)
- Interactive charts using Chart.js

Access: http://localhost:8000/dashboard

---

## 🔧 Configuration

.env example
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/frauddb
API_TOKEN=your_secure_token
JWT_SECRET=your_jwt_secret
REVIEW_THR=0.65
TX_THR=0.50
LOG_LEVEL=INFO
```

Threshold Tuning
- Higher threshold → fewer false positives
- Lower threshold → more aggressive detection

```bash
REVIEW_THR=0.80  # Conservative (High precision)
REVIEW_THR=0.50  # Aggressive (High recall)
```

---

## 🚢 Deployment

### Docker (Production)
```bash
make deploy-prod
# or manually
docker-compose -f docker-compose.prod.yml up -d --build
```

### Cloud Deployment

AWS ECS / Fargate
```bash
docker build -t fraud-detector:latest ./backend
docker tag fraud-detector:latest YOUR_ECR_URI/fraud-detector:latest
docker push YOUR_ECR_URI/fraud-detector:latest
aws ecs update-service --cluster fraud-cluster --service fraud-api --force-new-deployment
```

Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/fraud-detector ./backend
gcloud run deploy fraud-api --image gcr.io/YOUR_PROJECT/fraud-detector --platform managed
```

---

## 📈 Monitoring & Observability

- Prometheus Metrics: Latency (p50/p95/p99), inference time
- Grafana Dashboards: Fraud rate visualization
- Structured Logging: JSON logs with correlation IDs
- Alerts (Prometheus Rule Example):
```yaml
- alert: HighFraudRate
  expr: fraud_rate > 0.1
  for: 5m
  annotations:
    summary: "Fraud rate exceeded 10%"
```

---

## 🔒 Security Checklist

✅ Token & JWT Authentication  
✅ 30 req/min Rate Limiting  
✅ Input Validation & Schema Enforcement  
✅ SQL Injection Prevention via ORM  
✅ Secrets via .env  
✅ TLS (HTTPS) for Production

---

## 🛠️ Development

```text
fraud-detector/
├── backend/
│   ├── app.py
│   ├── models/
│   ├── pipelines/
│   ├── rules/
│   ├── db/
│   └── utils/
├── scripts/
│   ├── train_reviews.py
│   ├── train_tx.py
│   └── prepare_data.py
├── tests/
│   ├── test_api.py
│   ├── test_features.py
│   └── load_test.py
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
├── docker-compose.yml
└── Makefile
```

---

## 🧩 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Code Style
- Follow PEP 8
- Run `make lint` before committing
- Include tests for all new features

---

## 📚 Documentation

- docs/API.md — API Reference
- docs/MODELS.md — Model Details
- docs/DEPLOYMENT.md — Deployment Instructions
- docs/FEATURES.md — Feature Engineering

---

## 🎯 Roadmap

| Version | Features |
|--------:|----------|
| v2.0 (Q2 2025) | BERT Review Analysis, GNN for user graph, Blockchain traceability |
| v3.0 (Q4 2025) | Image authenticity, Multi-language support, Federated learning |

---

## 📊 Performance Benchmarks

| Metric | Value |
|-------:|-------|
| API Latency (p95) | < 100 ms |
| Throughput | 500 req/s |
| Model Inference | < 20 ms |
| DB Query | < 5 ms |
| Uptime | 99.9% |

---

## 🤝 Support & Community

- GitHub Issues: https://github.com/yourusername/fraud-detector/issues
- Discussions / Q&A
- support@yourcompany.com

---

## 📄 License
This project is licensed under the MIT License — see LICENSE.

---

## 🙏 Acknowledgments
- scikit-learn — ML Algorithms
- Flask — Web Framework
- PostgreSQL — Database
- Docker — Containerization
- Grafana + Prometheus — Monitoring

---

## 👨‍💻 Author

Ayush Kumar Singh  
AI/ML + Automation Engineer | LangChain • AutoGen • Cloud AI • Full-Stack Intelligent Systems  
GitHub: https://github.com/AyushKumar-Singh  
LinkedIn: https://linkedin.com/in/ayushkumarsingh  
Email: ayush@example.com

---

### 📸 Screenshots

Dashboard  
![Dashboard Screenshot](docs/images/dashboard.png)

API Response  
![API Example](docs/images/api_response.png)

Grafana Metrics  
![Grafana Monitoring](docs/images/grafana.png)

---

⭐ If you found this project helpful, please star it on GitHub!

<p align="center">Made with ❤️ by Ayush Kumar Singh for a safer e-commerce ecosystem</p>