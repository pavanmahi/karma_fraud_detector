from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import os
import joblib
from typing import List, Dict

# Load or train a local sentence transformer model
MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDING_DIM = 384

# === Curated content pools for both posts and comments ===
normal_texts = [
    # Comments
    "Great discussion, thanks for posting!",
    "Insightful post, learned something new.",
    "Well explained.",
    "Nice analysis!",
    "Really enjoyed reading this!",
    "Good find!",
    "Appreciate the details!",
    "Thanks for the update.",
    "Helpful explanation.",
    "Clear and concise.",
    "Agreed.",
    "Interesting!",
    "Makes sense.",
    "This is helpful.",
    "Thanks!",
    "Nice!",
    "Fair point.",
    "True that.",
    # Posts
    "Exploring the latest tech trends in AI.",
    "My experience with open source contributions.",
    "Tips for effective remote work.",
    "How to stay productive as a developer.",
    "A review of the best programming languages in 2024.",
    "Lessons learned from my first hackathon.",
    "How to build a personal portfolio website.",
    "Understanding the basics of machine learning.",
    "Why code reviews matter in software teams.",
    "Best resources for learning Python."
]

suspicious_texts = [
    # Comments
    "Insane",
    "Fire post!",
    "Unreal",
    "Mind blown!",
    "Crazy good!",
    "This hits, up!",
    "Epic, more pls!",
    "Legend post!",
    "Wild, upvote!",
    "Major W!",
    "Gold content!",
    "Hype this!",
    "Wow",
    "Viral vibes!",
    "Straight fire!",
    "Facts, up!",
    "This slaps!",
    "Banger post!",
    "Peak",
    "Truth, vote!",
    "King move!",
    "No cap, up!",
    "Lit content!",
    "Needed this, up!",
    "Quick",
    "Short and sweet!",
    "Up this now!",
    "Keep it up!",
    "Nice, again!",
    # Posts
    "Unbelievable trick to get more followers!",
    "Boost your karma instantly with this method.",
    "You won't believe this hack for upvotes.",
    "Get rich quick with this simple step.",
    "Secret to viral posts revealed!",
    "How I gained 1000 followers in a week!",
    "This one trick will change your life!",
    "Earn karma fast with this method!",
    "Top secret upvote strategy!",
    "Double your upvotes overnight!"
]

spam_texts = [
    # Comments
    "Upvote me now",
    "Check my page",
    "Pls upvote fast",
    "Boost this post",
    "Click my link",
    "Vote me up",
    "Sub for sub",
    "Need karma fast",
    "Karma farming",
    "Upvote exchange",
    "New here, need karma",
    "Follow back",
    "Drop an upvote!",
    "Karma needed ASAP!",
    "Link in bio!",
    "Upvote for upvote!",
    "Pls boost me!",
    "Check this out!",
    "Need votes now!",
    "Support my post!",
    "Follow me quick!",
    "Karma trade?",
    "Vote this up!",
    "Join my page!",
    "Upvote my stuff!",
    "Help me grow!",
    "Click here now!",
    "Karma plz!",
    # Posts
    "Upvote me and I'll upvote you back!",
    "Need karma fast, help me out!",
    "Join my upvote group for instant karma.",
    "Let's trade upvotes, comment below!",
    "Karma exchange, DM me now!",
    "Upvote for upvote, guaranteed!",
    "Help me reach 1000 karma today!",
    "Instant upvotes, just comment!",
    "Karma farming, join now!",
    "Upvote train, hop on!"
]

# Label creation
train_texts = normal_texts + suspicious_texts + spam_texts
spam_labels = [0]*len(normal_texts) + [0]*len(suspicious_texts) + [1]*len(spam_texts)
loweffort_labels = [0]*len(normal_texts) + [1]*len(suspicious_texts) + [1]*len(spam_texts)

# === Main NLP Analyzer Class ===
class ContentNLPAnalyzer:
    """
    NLP analyzer for both comments and posts. Provides spam and low-effort scores.
    Use .analyze(text) for any content (comment or post).
    """
    def __init__(self, model_path=None, spam_model_path=None, loweffort_model_path=None):
        self.model = SentenceTransformer(MODEL_NAME)
        # Load or initialize spam/low-effort classifiers
        if spam_model_path and os.path.exists(spam_model_path):
            self.spam_clf = joblib.load(spam_model_path)
        else:
            self.spam_clf = RandomForestClassifier()
        if loweffort_model_path and os.path.exists(loweffort_model_path):
            self.loweffort_clf = joblib.load(loweffort_model_path)
        else:
            self.loweffort_clf = RandomForestClassifier()
        # Sentiment classifier removed for now

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)

    def analyze(self, text: str) -> Dict[str, float]:
        emb = self.embed([text])[0].reshape(1, -1)
        # Predict spam and low-effort scores
        spam_score = float(self.spam_clf.predict_proba(emb)[0, 1]) if hasattr(self.spam_clf, 'predict_proba') else 0.0
        low_effort_score = float(self.loweffort_clf.predict_proba(emb)[0, 1]) if hasattr(self.loweffort_clf, 'predict_proba') else 0.0
        # Sentiment logic removed for now
        return {
            'spam_score': spam_score,
            'low_effort_score': low_effort_score
        }

# For backward compatibility
CommentNLPAnalyzer = ContentNLPAnalyzer

# Utility to train spam/low-effort classifiers (run once, save models)
def train_comment_classifiers(train_texts: List[str], spam_labels: List[int], loweffort_labels: List[int], save_dir: str):
    model = SentenceTransformer(MODEL_NAME)
    X = model.encode(train_texts)
    spam_clf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X, spam_labels)
    loweffort_clf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X, loweffort_labels)
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(spam_clf, os.path.join(save_dir, 'spam_clf.pkl'))
    joblib.dump(loweffort_clf, os.path.join(save_dir, 'loweffort_clf.pkl'))
    print('Spam and low-effort classifiers (RandomForest) saved to', save_dir)

# Utility to train a robust sentiment classifier
def train_sentiment_classifier(train_texts: List[str], sentiment_labels: List[int], save_dir: str):
    model = SentenceTransformer(MODEL_NAME)
    X = model.encode(train_texts)
    sentiment_clf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X, sentiment_labels)
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(sentiment_clf, os.path.join(save_dir, 'sentiment_clf.pkl'))
    print('Sentiment classifier (RandomForest) saved to', save_dir)

# === Main section for training (optional CLI) ===
if __name__ == '__main__':
    save_dir = os.path.join(os.path.dirname(__file__), '../model')
    print('Training spam and low-effort classifiers...')
    train_comment_classifiers(train_texts, spam_labels, loweffort_labels, save_dir)
    # For sentiment, you need to provide sentiment_labels (e.g., 1 for positive, 0 for negative)
    # Example: sentiment_labels = [1]*len(normal_texts) + [0]*len(spam_texts) + [0]*len(suspicious_texts)
    # Uncomment and edit the following lines to train sentiment:
    # sentiment_labels = [1]*len(normal_texts) + [0]*len(suspicious_texts) + [0]*len(spam_texts)
    # print('Training sentiment classifier...')
    # train_sentiment_classifier(train_texts, sentiment_labels, save_dir) 