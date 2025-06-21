import sys
import os
import json
import numpy as np
from joblib import load
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.feature_extractor import extract_features_batch
from app.nlp_utils import ContentNLPAnalyzer

MODEL_PATH = 'model/model.pkl'
FEATURE_NAMES_PATH = 'model/feature_names.json'

REASONS = {
    'young_upvote_ratio': 'Upvote from new account',
    'upvote_burst_count': 'Unusual burst of karma gain',
    'upvote_concentration': 'Upvote from bot-like account',
}

THRESHOLDS = {
    'young_upvote_ratio': 0.3,
    'upvote_burst_count': 1,
    'upvote_concentration': 0.5,
}

RECOMMENDATION_MAP = {0: 'clean', 1: 'flagged', 2: 'banned'}

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
    'nice': 0.6, 'cool': 0.6, 'good': 0.6, 'great': 0.6, 'awesome': 0.6, 'fire': 0.6, 'insane': 0.5, 'wild': 0.7, 'lit': 0.7, 'banger': 0.7,
    'amazing': 0.5, 'sick': 0.6, 'dope': 0.7, 'based': 0.6
}


def find_words(text, word_dict):
    found = []
    text_lower = text.lower()
    for word, score in word_dict.items():
        # Use word boundaries for words, but allow emojis and phrases
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower) or word in text_lower:
            found.append((word, score))
    return found

def main():
    input_path = 'data/newtest_users.json'
    with open(input_path) as f:
        user_logs = json.load(f)
    model = load(MODEL_PATH)
    with open(FEATURE_NAMES_PATH) as f:
        feature_names = json.load(f)
    X_dicts = extract_features_batch(user_logs)
    X = np.array([[row[f] for f in feature_names] for row in X_dicts])
    probs = model.predict_proba(X)
    preds = model.predict(X)
    results = []
    # Initialize NLP analyzer for per-activity spam detection
    nlp_analyzer = ContentNLPAnalyzer(
        spam_model_path='model/spam_clf.pkl',
        loweffort_model_path='model/loweffort_clf.pkl'
    )
    for i, user in enumerate(user_logs):
        user_id = user.get('user_id', f'user_{i}')
        features = X_dicts[i]
        fraud_score = float(probs[i, 2])
        suspicious_activities = []
        # Check for suspicious activities based on feature thresholds (upvotes)
        for feat, reason in REASONS.items():
            val = features.get(feat, 0)
            threshold = THRESHOLDS[feat]
            if val > threshold:
                upvotes = [a for a in user.get('karma_log', []) if a['type'] == 'upvote_received']
                if upvotes:
                    suspicious_activities.append({
                        'activity_id': upvotes[0]['activity_id'],
                        'reason': reason,
                        'score': round(val, 2)
                    })
        # --- New suspicious activity checks ---
        # Mutual upvotes
        if features.get('mutual_upvote_count', 0) >= 1:
            suspicious_activities.append({
                'reason': 'High number of mutual upvotes',
                'score': features['mutual_upvote_count']
            })
        # High post spam score
        if features.get('avg_post_spam_score', 0) > 0.7:
            suspicious_activities.append({
                'reason': 'High average post spam score',
                'score': round(features['avg_post_spam_score'], 2)
            })
        # Post burstiness
        if features.get('post_burst_count', 0) > 2:
            suspicious_activities.append({
                'reason': 'Burst of posts in short time',
                'score': features['post_burst_count']
            })
        # Upvote sent burstiness
        if features.get('upvote_sent_burst_count', 0) > 2:
            suspicious_activities.append({
                'reason': 'Burst of upvotes sent in short time',
                'score': features['upvote_sent_burst_count']
            })
        # Check for only one type of activity
        activity_types = set(a['type'] for a in user.get('karma_log', []))
        if len(activity_types) == 1:
            only_type = list(activity_types)[0]
            suspicious_activities.append({
                'reason': f'Only {only_type} type of activity is suspiciouos',
                'score': 1.0
            })
        # Check for spam/vague words in comments and posts
        comments = [a for a in user.get('karma_log', []) if a['type'] == 'comment']
        posts = [a for a in user.get('karma_log', []) if a['type'] == 'post_created']
        for c in comments + posts:
            found_spam = find_words(c.get('content', ''), spam_words)
            for word, score in found_spam:
                suspicious_activities.append({
                    'activity_id': c['activity_id'],
                    'reason': f"Spam word '{word}' detected",
                    'score': score
                })
            found_vague = find_words(c.get('content', ''), vague_words)
            for word, score in found_vague:
                suspicious_activities.append({
                    'activity_id': c['activity_id'],
                    'reason': f"Vague word '{word}' detected",
                    'score': score
                })
            # NLP-based spam detection
            nlp_result = nlp_analyzer.analyze(c.get('content', ''))
            if nlp_result['spam_score'] > 0.6:
                suspicious_activities.append({
                    'activity_id': c['activity_id'],
                    'reason': f"NLP spam score high ({nlp_result['spam_score']:.2f})",
                    'score': round(nlp_result['spam_score'], 2)
                })
        if fraud_score < 0.2:
            status = 'clean'
        elif fraud_score < 0.5:
            status = 'flagged'
        else:
            status = 'banned recommendation'
        results.append({
            'user_id': user_id,
            'fraud_score': round(fraud_score, 3),
            'suspicious_activities': suspicious_activities,
            'status': status
        })
    print('Result:')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main() 