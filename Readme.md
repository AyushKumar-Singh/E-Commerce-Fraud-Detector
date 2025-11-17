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

---

## 🎨 Frontend Setup (Optional React Dashboard)

```bash
cd frontend
npm install
npm run dev
```

---

## 🐳 Docker Deployment

```bash
docker compose up --build
```

Stop:
```bash
docker compose down
```

---

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
```

---

## 🧪 Testing

```bash
pytest
```

---

## 🧭 Future Enhancements
- BERT/LSTM for more accurate review authenticity detection  
- Blockchain verification for transaction integrity  
- Advanced fraud dashboard with alerts  
- SaaS multi-tenant architecture  
- Online learning pipeline for continuous training  
- Image-based fake product detection  

---

## 🤝 Contributing  
Pull requests are welcome — ensure that tests pass and code is formatted properly.

---

## 👤 Author  
**Ayush Kumar Singh**  
AI Systems Architect & LLM Infrastructure Engineer  
LinkedIn: ayush-kumar-singh  
GitHub: AyushKumar-Singh

