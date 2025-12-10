@echo off
echo Installing dependencies...
python3 -m pip install --user flask flask-cors flask-limiter sqlalchemy python-dotenv pyjwt joblib scikit-learn pandas numpy nltk

echo.
echo Starting backend server...
cd backend
python3 app.py
