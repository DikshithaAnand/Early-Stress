# 🧠 MindScan — AI Early Mental Stress Detection System

A full-stack AI web application that predicts user stress levels based on daily lifestyle inputs and provides personalized recommendations.This application will detect the stress based on your daily activities.It will help you to know your stress level.

---

## 📁 Project Structure

```
stress-app/
├── frontend/
│   └── index.html          ← Complete frontend (single-file app)
│
├── backend/
│   ├── main.py             ← FastAPI backend (all routes)
│   └── requirements.txt    ← Python dependencies
│
└── ml_model/
    └── train_model.py      ← ML model training script
```

---

## 🚀 Quick Start

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Train the ML Model

```bash
cd ml_model
python train_model.py
```

This generates `stress_model.pkl` in the `ml_model/` folder.

### Step 3: Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`
Swagger docs at: `http://localhost:8000/docs`

### Step 4: Open the Frontend

Simply open `frontend/index.html` in your browser.

> **Note:** The frontend works in **demo mode** even without the backend.  
> A rule-based engine provides predictions when the API is unavailable.

---

## 🔑 Demo Account

Click **"Use Demo Account"** on the login page to log in instantly without creating an account.

- Email: `demo@mindscan.ai`
- Password: `demo123`

---

## 🤖 AI Model Details

| Feature | Description |
|---|---|
| Algorithm | Random Forest Classifier |
| Input Features | sleep_hours, study_hours, social_media_hours, screen_time, mood_level |
| Output Classes | Low Stress (0), Moderate Stress (1), High Stress (2) |
| Training Samples | 3,000 synthetic samples |
| Expected Accuracy | ~88–92% |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Create a new user account |
| `POST` | `/login` | Login and get JWT token |
| `POST` | `/predict` | Predict stress level (requires auth) |
| `GET` | `/me` | Get current user info |

### Example: Predict Stress

```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sleep_hours": 5,
    "study_hours": 12,
    "social_media_hours": 4,
    "screen_time": 10,
    "mood_level": 2
  }'
```

### Example Responses

```json
{
  "level": "High Stress",
  "color": "#f87171",
  "emoji": "😔",
  "gauge": 90,
  "tips": [
    "Take a meaningful break from work or studies today.",
    "Talk to someone you trust — don't carry this alone.",
    ...
  ],
  "probabilities": {
    "low": 4.2,
    "moderate": 16.1,
    "high": 79.7
  }
}
```

---

## 💻 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Canvas API (custom gauge), Chart.js |
| Backend | Python, FastAPI, Uvicorn |
| ML Model | Scikit-Learn, Random Forest |
| Auth | JWT (HS256), Password Hashing (SHA-256) |
| Storage | JSON file-based (swap with PostgreSQL for production) |

---

## 🎨 Design

The project follows a **calming, minimal, and mental-health-focused design system** to provide users with a peaceful and supportive experience.

- **Color Palette:** Sage green, soft teal, warm beige, and earth tones
- **Typography:** Playfair Display for headings and DM Sans for body text
- **Theme:** Clean, minimal, emotionally supportive, and wellness-oriented
- **Layout:** Single-page application (SPA) with smooth multi-page navigation

---

## 🔒 Security Features

- Password hashing (SHA-256)
- JWT token authentication with 24h expiry
- Protected prediction endpoint
- Input validation via Pydantic

---

## ⚠️ Disclaimer

MindScan is designed for **early awareness and educational purposes only**.  
It is NOT a clinical diagnostic tool. For serious mental health concerns, please consult a licensed mental health professional.

---
