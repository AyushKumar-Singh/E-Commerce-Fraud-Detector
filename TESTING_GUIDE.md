# Testing Guide - E-Commerce Fraud Detector

Comprehensive guide for testing the fraud detection system.

## Quick Health Check

```powershell
# Backend health
Invoke-RestMethod http://localhost:8000/health

# Expected:
# status: healthy
# models_loaded: review_model, tx_model, catboost_model
# database: connected
```

---

## API Testing

### Prerequisites

Set up authentication:
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key" = "vUfIt9RDa2BLiYEcmwSp5VoCkNlQMgbT"
}
```

### Review Prediction

```powershell
# Test genuine review
$body = '{"user_id": 1001, "product_id": "PROD-001", "review_text": "Good product, meets expectations. Delivery was on time.", "rating": 4}'
Invoke-RestMethod -Uri "http://localhost:8000/predict/review" -Method Post -Headers $headers -Body $body

# Test suspicious review (should flag)
$body = '{"user_id": 1002, "product_id": "PROD-002", "review_text": "perfect", "rating": 5}'
Invoke-RestMethod -Uri "http://localhost:8000/predict/review" -Method Post -Headers $headers -Body $body
```

### Transaction Prediction

```powershell
# Normal transaction
$body = '{"user_id": 1001, "amount": 1500, "currency": "INR", "channel": "web"}'
Invoke-RestMethod -Uri "http://localhost:8000/predict/transaction" -Method Post -Headers $headers -Body $body

# High-value transaction (should flag)
$body = '{"user_id": 1001, "amount": 50000, "currency": "INR", "channel": "web"}'
Invoke-RestMethod -Uri "http://localhost:8000/predict/transaction" -Method Post -Headers $headers -Body $body
```

### Dashboard Endpoints

```powershell
# Get stats
Invoke-RestMethod -Uri "http://localhost:8000/dashboard/api/stats" -Headers $headers

# Get trends
Invoke-RestMethod -Uri "http://localhost:8000/dashboard/api/trends?days=30" -Headers $headers

# Get all reviews
Invoke-RestMethod -Uri "http://localhost:8000/dashboard/api/all-reviews" -Headers $headers
```

---

## Frontend Testing

### Access Points
| Environment | URL |
|-------------|-----|
| Development | http://localhost:3000 or http://localhost:5173 |
| Docker | http://localhost:3000 |

### Test Checklist

- [ ] Login page loads
- [ ] Authentication with API token works
- [ ] Dashboard displays stats
- [ ] Review Analysis page works
- [ ] Add Review form submits correctly
- [ ] Transaction Analysis page works  
- [ ] Navigation between pages works

---

## Docker Testing

### Start Services
```powershell
docker-compose -f infra/compose/docker-compose.yml up -d
docker-compose -f infra/compose/docker-compose.yml ps
```

### Test Containerized API
```powershell
# Wait for services to start
Start-Sleep -Seconds 30

# Health check
Invoke-RestMethod http://localhost:8000/health
```

### Check Logs
```powershell
docker-compose -f infra/compose/docker-compose.yml logs api
docker-compose -f infra/compose/docker-compose.yml logs frontend
```

---

## Kubernetes Testing (Minikube)

### Prerequisites
```powershell
minikube start
minikube addons enable ingress
```

### Deploy & Test
```powershell
# Build images in Minikube
minikube docker-env | Invoke-Expression
docker build -t fraud-detector-api:latest ./backend
docker build -t fraud-detector-ui:latest ./frontend

# Deploy
kubectl apply -f infra/k8s/

# Check pods
kubectl get pods -n fraud-detector

# Port forward for testing
kubectl port-forward svc/backend -n fraud-detector 8000:8000
```

---

## Test Data Scenarios

### Reviews That Should Be Flagged
| Review | Expected Score |
|--------|---------------|
| "perfect" (1 word, 5 stars) | ~1.0 (FAKE) |
| "AMAZING!!! BEST EVER!!!" (all caps) | >0.05 |
| Empty or very short text | >0.5 |

### Reviews That Should Pass
| Review | Expected Score |
|--------|---------------|
| Detailed 3-4 sentence review | ~0.0 (GENUINE) |
| Balanced pros/cons | ~0.0 |
| Moderate rating (3-4 stars) | Low score |

### Transactions That Should Be Flagged
| Amount | User Type | Expected |
|--------|-----------|----------|
| >₹20,000 | New user | FLAG |
| >₹50,000 | Any user | FLAG |
| Rapid multiple transactions | Any | FLAG |

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ERR_CONNECTION_REFUSED` | Start backend: `python backend/app.py` |
| `401 Unauthorized` | Check API token in headers |
| `500 Internal Server Error` | Check backend logs for details |
| CORS errors | Verify frontend URL in backend CORS config |
| Docker build fails | Check .dockerignore, run `docker system prune` |

---

## Performance Benchmarks

| Metric | Expected |
|--------|----------|
| Health check | <50ms |
| Review prediction | <200ms |
| Transaction prediction | <200ms |
| Model load time | 2-5 seconds |

---

## Related Documentation

- [QUICK_START.md](QUICK_START.md) - Get running quickly
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to production
- [Readme.md](Readme.md) - Project overview
