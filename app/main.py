from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import json
import numpy as np
from joblib import load
import os
import re
from app.feature_extractor import extract_features_batch
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.nlp_utils import ContentNLPAnalyzer

# Load config
CONFIG_PATH = 'config.json'
MODEL_PATH = 'model/model.pkl'
FEATURE_NAMES_PATH = 'model/feature_names.json'

# --- Config loading ---
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "fraud_score_thresholds": {"clean": 0.2, "flagged": 0.6},
        "version": "1.0.0"
    }

config = load_config()

# --- Model loading ---
model = load(MODEL_PATH)
with open(FEATURE_NAMES_PATH) as f:
    feature_names = json.load(f)

# --- Spam/vague word dicts (can be moved to config) ---
spam_words = {
    "upvote pls": 1.0, "pls upvote": 1.0, "follow me": 1.0, "check my profile": 0.9,
    "dm me": 0.8, "please upvote": 1.0, "click my link": 0.9, "vote me": 1.0,
    "top post": 0.8, "boost": 0.8, "🔥": 0.4, "💯": 0.4, "wow": 0.3, "lol": 0.2,
    "this slaps": 0.4, "facts": 0.3, "check out my page": 0.9,
    "drop an upvote": 1.0, "karma needed": 1.0, "link in bio": 0.9, "upvote for upvote": 1.0,
    "pls boost me": 0.9, "check this out": 0.8, "need votes": 1.0, "support my post": 0.9,
    "sub for sub": 1.0, "f4f": 0.9, "like4like": 0.9, "comment4comment": 0.9
}
vague_words = {
    'nice': 0.6, 'cool': 0.6, 'good': 0.6, 'great': 0.6, 'awesome': 0.6, 'fire': 0.6,
    'insane': 0.5, 'wild': 0.7, 'lit': 0.7, 'banger': 0.7,
    'amazing': 0.5, 'sick': 0.6, 'dope': 0.7, 'based': 0.6
}

# --- Pydantic models ---
class KarmaActivity(BaseModel):
    activity_id: str
    type: str
    content: Optional[str] = None
    from_user: Optional[str] = None
    from_user_age_days: Optional[int] = None
    timestamp: str
    source: Optional[str] = None
    post_id: Optional[str] = None

class AnalyzeRequest(BaseModel):
    user_id: str
    karma_log: List[KarmaActivity]

class SuspiciousActivity(BaseModel):
    activity_id: str
    reason: str
    score: float

class AnalyzeResponse(BaseModel):
    user_id: str
    fraud_score: float
    suspicious_activities: List[SuspiciousActivity]
    status: str

# --- Utility functions ---
def find_words(text, word_dict):
    found = []
    text_lower = text.lower()
    for word, score in word_dict.items():
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower) or word in text_lower:
            found.append((word, score))
    return found

# Initialize NLP analyzer for per-activity spam detection
nlp_analyzer = ContentNLPAnalyzer(
    spam_model_path='model/spam_clf.pkl',
    loweffort_model_path='model/loweffort_clf.pkl'
)

def explain_activities(user, features):
    suspicious_activities = []
    # Upvote-based
    upvotes = [a for a in user.karma_log if a.type == 'upvote_received']
    if features.get('young_upvote_ratio', 0) > 0.3 and upvotes:
        suspicious_activities.append({
            'activity_id': upvotes[0].activity_id,
            'reason': 'Upvote from new account',
            'score': round(features['young_upvote_ratio'], 2)
        })
    if features.get('upvote_burst_count', 0) > 1 and upvotes:
        suspicious_activities.append({
            'activity_id': upvotes[0].activity_id,
            'reason': 'Unusual burst of karma gain',
            'score': round(features['upvote_burst_count'], 2)
        })
    if features.get('upvote_concentration', 0) > 0.5 and upvotes:
        suspicious_activities.append({
            'activity_id': upvotes[0].activity_id,
            'reason': 'Upvote from bot-like account',
            'score': round(features['upvote_concentration'], 2)
        })
    # --- New suspicious activity checks ---
    if features.get('mutual_upvote_count', 0) >= 2:
        suspicious_activities.append({
            'reason': 'High number of mutual upvotes',
            'score': features['mutual_upvote_count']
        })
    if features.get('avg_post_spam_score', 0) > 0.7:
        suspicious_activities.append({
            'reason': 'High average post spam score',
            'score': round(features['avg_post_spam_score'], 2)
        })
    if features.get('post_burst_count', 0) > 2:
        suspicious_activities.append({
            'reason': 'Burst of posts in short time',
            'score': features['post_burst_count']
        })
    if features.get('upvote_sent_burst_count', 0) > 2:
        suspicious_activities.append({
            'reason': 'Burst of upvotes sent in short time',
            'score': features['upvote_sent_burst_count']
        })
    # Only one type of activity
    activity_types = set(a.type for a in user.karma_log)
    if len(activity_types) == 1:
        only_type = list(activity_types)[0]
        suspicious_activities.append({
            'reason': f'Only {only_type} type of activity is suspiciouos',
            'score': 1.0
        })
    # Spam/vague word detection for comments and posts
    comments = [a for a in user.karma_log if a.type == 'comment']
    posts = [a for a in user.karma_log if a.type == 'post_created']
    for c in comments + posts:
        found_spam = find_words((c.content or ''), spam_words)
        for word, score in found_spam:
            suspicious_activities.append({
                'activity_id': c.activity_id,
                'reason': f"Spam word '{word}' detected",
                'score': score
            })
        found_vague = find_words((c.content or ''), vague_words)
        for word, score in found_vague:
            suspicious_activities.append({
                'activity_id': c.activity_id,
                'reason': f"Vague word '{word}' detected",
                'score': score
            })
        # NLP-based spam detection
        nlp_result = nlp_analyzer.analyze(c.content or '')
        if nlp_result['spam_score'] > 0.6:
            suspicious_activities.append({
                'activity_id': c.activity_id,
                'reason': f"NLP spam score high ({nlp_result['spam_score']:.2f})",
                'score': round(nlp_result['spam_score'], 2)
            })
    return suspicious_activities

def get_status(fraud_score):
    if fraud_score < 0.25:
        return 'clean'
    elif fraud_score < 0.6:
        return 'flagged'
    else:
        return 'banned_recommendation'

# --- FastAPI app ---
app = FastAPI(title="Karma Fraud Detector", version=config.get('version', '1.0.0'))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post('/api/analyze', response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    user_dict = request.dict()
    X_dicts = extract_features_batch([user_dict])
    features = X_dicts[0]
    X = np.array([[features[f] for f in feature_names]])
    fraud_score = float(model.predict_proba(X)[0, 2])
    suspicious_activities = explain_activities(request, features)
    status = get_status(fraud_score)
    return AnalyzeResponse(
        user_id=request.user_id,
        fraud_score=round(fraud_score, 3),
        suspicious_activities=suspicious_activities,
        status=status
    )

@app.get('/api/health', response_class=JSONResponse)
def health():
    return {"status": "Ok"}

@app.get('/api/version', response_class=JSONResponse)
def version():
    return {"version": config.get('version', '1.0.0')}

# Mount static files only if they exist (for local development)
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="spa")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000) 
    