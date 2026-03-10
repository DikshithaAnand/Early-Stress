"""
AI Early Mental Stress Detection System - FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import pickle
import numpy as np
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta

# JWT (simple implementation without external libraries)
import base64
import hmac
import hashlib as hl
import time

app = FastAPI(
    title="AI Stress Detection API",
    description="Early Mental Stress Detection using Machine Learning",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Simple file-based user store (replace with DB)
USERS_FILE = "users.json"
SECRET_KEY = "stress-detection-secret-key-2024"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ─────────────────────────────────────────────
# Simple JWT implementation
def create_token(email: str) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({
        "sub": email,
        "exp": time.time() + 86400  # 24h
    }).encode()).decode().rstrip("=")
    signature_input = f"{header}.{payload}"
    sig = hmac.new(SECRET_KEY.encode(), signature_input.encode(), hl.sha256).hexdigest()
    return f"{header}.{payload}.{sig}"

def verify_token(token: str) -> Optional[str]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, sig = parts
        signature_input = f"{header}.{payload}"
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_input.encode(), hl.sha256).hexdigest()
        if sig != expected_sig:
            return None
        pad = 4 - len(payload) % 4
        payload_data = json.loads(base64.urlsafe_b64decode(payload + "=" * pad))
        if payload_data.get("exp", 0) < time.time():
            return None
        return payload_data.get("sub")
    except Exception:
        return None

# ─────────────────────────────────────────────
# Load ML Model
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "..", "ml_model", "stress_model.pkl")
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None

ml_model = load_model()

# ─────────────────────────────────────────────
# Pydantic Models
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class PredictRequest(BaseModel):
    sleep_hours: float       # 0 - 12
    study_hours: float       # 0 - 18
    social_media_hours: float  # 0 - 12
    screen_time: float       # 0 - 18
    mood_level: int          # 1=Very Stressed, 2=Stressed, 3=Neutral, 4=Happy, 5=Very Happy

# ─────────────────────────────────────────────
# Auth dependency
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return email

# ─────────────────────────────────────────────
# Stress rules engine (fallback if no model)
def rule_based_prediction(sleep, study, social_media, screen, mood):
    score = 0
    # Sleep scoring (lower is worse)
    if sleep >= 7: score += 0
    elif sleep >= 5: score += 2
    else: score += 4

    # Study hours
    if study <= 6: score += 0
    elif study <= 10: score += 2
    else: score += 4

    # Social media
    if social_media <= 2: score += 0
    elif social_media <= 4: score += 1
    else: score += 3

    # Screen time
    if screen <= 5: score += 0
    elif screen <= 8: score += 1
    else: score += 2

    # Mood (inverted - 5=very happy=0 score, 1=very stressed=4 score)
    score += (5 - mood)

    if score <= 3: return 0   # Low
    elif score <= 8: return 1  # Moderate
    else: return 2             # High

def get_suggestions(level: int):
    suggestions = {
        0: {
            "level": "Low Stress",
            "color": "#4ade80",
            "emoji": "😊",
            "gauge": 20,
            "tips": [
                "Maintain your current routine — it's clearly working!",
                "Stay consistent with your sleep schedule.",
                "Keep up with physical activity or light exercise.",
                "Celebrate small wins to reinforce positive habits.",
                "Consider journaling to track your well-being over time."
            ]
        },
        1: {
            "level": "Moderate Stress",
            "color": "#fbbf24",
            "emoji": "😐",
            "gauge": 60,
            "tips": [
                "Improve your sleep schedule — aim for 7–8 hours nightly.",
                "Reduce screen time, especially 1 hour before bed.",
                "Practice deep breathing or meditation for 10 minutes daily.",
                "Break large tasks into smaller, manageable steps.",
                "Connect with a friend or family member today."
            ]
        },
        2: {
            "level": "High Stress",
            "color": "#f87171",
            "emoji": "😔",
            "gauge": 90,
            "tips": [
                "Take a meaningful break from work or studies today.",
                "Talk to someone you trust — don't carry this alone.",
                "Prioritize sleep above all else tonight.",
                "Limit social media and news consumption significantly.",
                "Consider speaking with a mental health professional — it's a sign of strength."
            ]
        }
    }
    return suggestions.get(level, suggestions[1])

# ─────────────────────────────────────────────
# Routes

@app.get("/")
def root():
    return {"message": "AI Stress Detection API is running", "version": "1.0.0"}

@app.post("/signup")
def signup(data: SignupRequest):
    users = load_users()
    if data.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[data.email] = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return {"message": "Account created successfully", "name": data.name}

@app.post("/login")
def login(data: LoginRequest):
    users = load_users()
    user = users.get(data.email)
    if not user or user["password"] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(data.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "name": user["name"],
        "email": user["email"]
    }

@app.post("/predict")
def predict(data: PredictRequest, current_user: str = Depends(get_current_user)):
    features = np.array([[
        data.sleep_hours,
        data.study_hours,
        data.social_media_hours,
        data.screen_time,
        data.mood_level
    ]])

    if ml_model:
        prediction = int(ml_model.predict(features)[0])
        probabilities = ml_model.predict_proba(features)[0].tolist()
    else:
        prediction = rule_based_prediction(
            data.sleep_hours, data.study_hours,
            data.social_media_hours, data.screen_time, data.mood_level
        )
        probabilities = [0.0, 0.0, 0.0]
        probabilities[prediction] = 1.0

    result = get_suggestions(prediction)
    result["probabilities"] = {
        "low": round(probabilities[0] * 100, 1),
        "moderate": round(probabilities[1] * 100, 1),
        "high": round(probabilities[2] * 100, 1)
    }
    result["inputs"] = data.dict()
    result["timestamp"] = datetime.now().isoformat()
    return result

@app.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    users = load_users()
    user = users.get(current_user, {})
    return {"name": user.get("name", ""), "email": current_user}
