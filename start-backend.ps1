# PowerShell script to start backend
Write-Host "Installing dependencies..." -ForegroundColor Green
python3 -m pip install --user flask flask-cors flask-limiter sqlalchemy python-dotenv pyjwt joblib scikit-learn pandas numpy nltk

Write-Host "`nStarting backend server..." -ForegroundColor Green
Set-Location backend
python3 app.py
