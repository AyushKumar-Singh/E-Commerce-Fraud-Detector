# Testing Guide - E-Commerce Fraud Detector

## ✅ All Systems Running

### Services Status
- ✅ **Backend API**: Running on http://localhost:8000
- ✅ **Frontend**: Running on http://localhost:3002
- ✅ **Database**: SQLite (auto-created)
- ✅ **Models**: Loaded successfully

## 🧪 Testing Checklist

### 1. Health Check Tests

#### Backend Health
```powershell
# Test backend is running
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "models_loaded": {
#     "review_model": true,
#     "tx_model": true
#   },
#   "database": "connected"
# }
```

### 2. Authentication Tests

#### Get API Token
```powershell
# Using the admin secret from .env
$body = @{secret="c7883e87ab7e0401ac908fa1f505af3054c763243519e47a579e31c403a151cd"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/auth/token" -Method POST -ContentType "application/json" -Body $body

# Expected: JWT token returned
# Save the token for use in subsequent requests
```

### 3. Frontend UI Tests

#### Login Page
1. Open http://localhost:3002 in your browser
2. You should be redirected to /login
3. Enter the admin secret: `c7883e87ab7e0401ac908fa1f505af3054c763243519e47a579e31c403a151cd`
4. Click "Sign In"
5. Should redirect to dashboard

#### Dashboard Page
1. After login, verify you see:
   - Stats cards (Today/Week/Month)
   - Trend charts
   - Top offenders
   - Recent flags

#### Predict Review Page
1. Navigate to /predict
2. Click on "Review" tab
3. Fill in the form:
   - User ID: 123
   - Product ID: PROD-456
   - Review Text: "This is an amazing product! Best purchase ever! Highly recommend to everyone! 5 stars!!!"
   - Rating: 5
4. Click "Analyze Review"
5. Verify prediction result is displayed

#### Predict Transaction Page
1. On /predict page, click "Transaction" tab
2. Fill in the form:
   - User ID: 123
   - Amount: 50000
   - Currency: INR
   - Channel: web
3. Click "Analyze Transaction"
4. Verify fraud score is displayed

### 4. API Endpoint Tests

#### Review Prediction
```powershell
# Get token first (save to $token variable)
$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key" = $token
}

$reviewBody = @{
    user_id = 123
    product_id = "PROD-456"
    review_text = "Amazing product! Best ever! Highly recommend!"
    rating = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict/review" -Method POST -Headers $headers -Body $reviewBody
```

#### Transaction Prediction
```powershell
$txBody = @{
    user_id = 123
    amount = 5000
    currency = "INR"
    channel = "web"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict/transaction" -Method POST -Headers $headers -Body $txBody
```

#### Dashboard Stats
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/dashboard/api/stats" -Method GET -Headers $headers
```

### 5. Test Data Scenarios

#### Suspicious Review (Should flag as fake)
```json
{
  "user_id": 999,
  "product_id": "PROD-123",
  "review_text": "AMAZING!!! BEST PRODUCT EVER!!! BUY NOW!!! 100% RECOMMENDED!!! FIVE STARS!!!!!",
  "rating": 5
}
```

#### Normal Review (Should be genuine)
```json
{
  "user_id": 100,
  "product_id": "PROD-456",
  "review_text": "Good product, meets my expectations. Delivery was on time. Would buy again.",
  "rating": 4
}
```

#### High-Value Transaction (Should flag)
```json
{
  "user_id": 1,
  "amount": 100000,
  "currency": "INR",
  "channel": "api"
}
```

#### Normal Transaction
```json
{
  "user_id": 50,
  "amount": 1500,
  "currency": "INR",
  "channel": "web"
}
```

## 🔍 Error Monitoring

### Backend Logs
Monitor the terminal where backend is running for any errors:
- Database connection issues
- Model prediction errors
- API request failures

### Frontend Console
Open browser DevTools (F12) and check:
- Console tab for JavaScript errors
- Network tab for failed API calls
- Ensure CORS is working (no CORS errors)

## 📊 Performance Tests

### Load Testing (Optional)
```powershell
# Install Artillery if needed
npm install -g artillery

# Run load test
artillery quick --count 10 --num 100 http://localhost:8000/health
```

## ✅ All Tests Passed Criteria

- ✅ Backend responds to /health endpoint
- ✅ Authentication works (token generation)
- ✅ Frontend loads without errors
- ✅ Login redirects to dashboard
- ✅ Review prediction works
- ✅ Transaction prediction works
- ✅ Dashboard displays data
- ✅ No CORS errors
- ✅ Models load successfully

## 🐛 Common Issues & Fixes

### Issue: "Connection refused" on localhost:8000
**Fix**: Ensure backend is running. Check terminal for errors.

### Issue: "401 Unauthorized" errors
**Fix**: Get a fresh token using /auth/token endpoint

### Issue: Frontend shows white screen
**Fix**: 
1. Check browser console for errors
2. Verify all files in frontend-react/src exist
3. Restart dev server: `npm run dev`

### Issue: "Module not found" errors
**Fix**: 
1. Stop dev server (Ctrl+C)
2. Run `npm install`
3. Restart: `npm run dev`

### Issue: CORS errors
**Fix**: Backend CORS is configured for localhost:3000-5173. Check your frontend port matches.

## 📝 Test Results Template

```
Date: _______________
Tester: _______________

Backend Tests:
[ ] Health check
[ ] Authentication
[ ] Review prediction
[ ] Transaction prediction
[ ] Dashboard stats

Frontend Tests:
[ ] Login page loads
[ ] Authentication works
[ ] Dashboard displays
[ ] Review form works
[ ] Transaction form works
[ ] Navigation works

Issues Found:
_______________________
_______________________

Notes:
_______________________
_______________________
```

## 🎯 Next Steps After Testing

1. Fix any identified issues
2. Add more test data
3. Configure production database (PostgreSQL)
4. Deploy to cloud (AWS/GCP)
5. Set up monitoring (Grafana)
6. Enable SSL/HTTPS
7. Configure production secrets

## Support

For issues, check:
- QUICK_START.md for setup instructions
- README.md for detailed documentation
- Backend logs for API errors
- Browser console for frontend errors
