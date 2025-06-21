import numpy as np
from typing import List, Dict, Any
from collections import Counter
import re
from datetime import datetime
from app.nlp_utils import ContentNLPAnalyzer

# Helper to robustly parse ISO timestamps
def parse_timestamp(ts: str) -> datetime:
    try:
        # Remove 'Z' if present
        if ts.endswith('Z'):
            ts = ts[:-1]
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.now()  # fallback, should log in production

# Initialize the NLP analyzer (load models if available)
nlp_analyzer = ContentNLPAnalyzer(
    spam_model_path='model/spam_clf.pkl',
    loweffort_model_path='model/loweffort_clf.pkl'
)

def extract_features(user_log: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts features from a user's karma log for fraud detection.
    Returns a feature dict for model input.
    """
    karma_log = user_log.get('karma_log', [])
    user_id = user_log.get('user_id', '')
    account_age_days = user_log.get('account_age_days', 10)

    upvotes = [a for a in karma_log if a['type'] == 'upvote_received']
    comments = [a for a in karma_log if a['type'] == 'comment']
    posts = [a for a in karma_log if a['type'] == 'post_created']
    upvotes_sent = [a for a in karma_log if a['type'] == 'upvote_sent']

    # Upvote features
    upvote_from_users = [a['from_user'] for a in upvotes]
    upvote_from_ages = [a.get('from_user_age_days', 10) for a in upvotes]
    upvote_counts = Counter(upvote_from_users)
    repeated_upvotes = sum(1 for c in upvote_counts.values() if c > 1)
    if len(upvotes) == 1:
        upvote_concentration = 0.0
        unique_upvoters_ratio = 0.0
    else:
        upvote_concentration = max(upvote_counts.values()) / max(1, len(upvotes)) if upvotes else 0.0
        unique_upvoters_ratio = len(set(upvote_from_users)) / max(1, len(upvotes)) if upvotes else 0.0
    young_upvote_ratio = sum(1 for age in upvote_from_ages if age is not None and age <= 7) / max(1, len(upvotes)) if upvotes else 0.0

    # Upvote burstiness (time between upvotes)
    upvote_times = [parse_timestamp(a['timestamp']) for a in upvotes]
    upvote_times_sorted = sorted(upvote_times)
    upvote_time_diffs = [
        (upvote_times_sorted[i+1] - upvote_times_sorted[i]).total_seconds()
        for i in range(len(upvote_times_sorted)-1)
    ] if len(upvote_times_sorted) > 1 else []
    avg_upvote_gap = np.mean(upvote_time_diffs) if upvote_time_diffs else 0.0
    min_upvote_gap = np.min(upvote_time_diffs) if upvote_time_diffs else 0.0
    upvote_burst_count = sum(1 for diff in upvote_time_diffs if diff < 3600)  # <1hr between upvotes

    # Comment NLP features (using real model)
    nlp_features = [nlp_analyzer.analyze(a['content']) for a in comments]
    avg_spam_score = np.mean([f['spam_score'] for f in nlp_features]) if nlp_features else 0.0
    avg_low_effort = np.mean([f['low_effort_score'] for f in nlp_features]) if nlp_features else 0.0

    # Comment/Upvote ratios
    comment_count = len(comments)
    upvote_count = len(upvotes)
    comment_to_upvote_ratio = comment_count / max(1, upvote_count)

    # Comment length statistics
    comment_lengths = [len(a['content']) for a in comments]
    avg_comment_length = np.mean(comment_lengths) if comment_lengths else 0.0
    median_comment_length = float(np.median(comment_lengths)) if comment_lengths else 0.0
    comment_burst_count = 0
    if len(comments) > 1:
        comment_times = [parse_timestamp(a['timestamp']) for a in comments]
        comment_times_sorted = sorted(comment_times)
        comment_time_diffs = [
            (comment_times_sorted[i+1] - comment_times_sorted[i]).total_seconds()
            for i in range(len(comment_times_sorted)-1)
        ]
        comment_burst_count = sum(1 for diff in comment_time_diffs if diff < 3600)  # <1hr between comments

    # --- Post features ---
    total_posts = len(posts)
    # Post burstiness (number of posts <1hr apart)
    post_burst_count = 0
    if len(posts) > 1:
        post_times = [parse_timestamp(a['timestamp']) for a in posts]
        post_times_sorted = sorted(post_times)
        post_time_diffs = [
            (post_times_sorted[i+1] - post_times_sorted[i]).total_seconds()
            for i in range(len(post_times_sorted)-1)
        ]
        post_burst_count = sum(1 for diff in post_time_diffs if diff < 3600)
    # Post NLP features
    post_nlp_features = [nlp_analyzer.analyze(a['content']) for a in posts]
    avg_post_spam_score = np.mean([f['spam_score'] for f in post_nlp_features]) if post_nlp_features else 0.0

    # --- Upvote sent features ---
    total_upvotes_sent = len(upvotes_sent)
    upvote_sent_targets = [a['to_user'] for a in upvotes_sent if 'to_user' in a]
    unique_upvote_targets = len(set(upvote_sent_targets)) if upvote_sent_targets else 0
    # Upvote sent burstiness (number of upvotes sent <1hr apart)
    upvote_sent_burst_count = 0
    if len(upvotes_sent) > 1:
        upvote_sent_times = [parse_timestamp(a['timestamp']) for a in upvotes_sent]
        upvote_sent_times_sorted = sorted(upvote_sent_times)
        upvote_sent_time_diffs = [
            (upvote_sent_times_sorted[i+1] - upvote_sent_times_sorted[i]).total_seconds()
            for i in range(len(upvote_sent_times_sorted)-1)
        ]
        upvote_sent_burst_count = sum(1 for diff in upvote_sent_time_diffs if diff < 3600)
    # Mutual upvote count (users who both sent and received upvotes with this user)
    upvote_from_users_set = set(a['from_user'] for a in upvotes if 'from_user' in a)
    upvote_sent_targets_set = set(upvote_sent_targets)
    mutual_upvote_count = len(upvote_from_users_set & upvote_sent_targets_set)

    # Feature vector
    features = {
        'user_id': user_id,
        'account_age_days': account_age_days,
        'total_comments': comment_count,
        'total_upvotes': upvote_count,
        'repeated_upvotes': repeated_upvotes,
        'upvote_concentration': upvote_concentration,
        'unique_upvoters_ratio': unique_upvoters_ratio,
        'young_upvote_ratio': young_upvote_ratio,
        'avg_upvote_gap': avg_upvote_gap,
        'min_upvote_gap': min_upvote_gap,
        'upvote_burst_count': upvote_burst_count,
        'avg_spam_score': avg_spam_score,
        'avg_low_effort': avg_low_effort,
        'comment_to_upvote_ratio': comment_to_upvote_ratio,
        'avg_comment_length': avg_comment_length,
        'median_comment_length': median_comment_length,
        'comment_burst_count': comment_burst_count,
        # --- Post features ---
        'total_posts': total_posts,
        'post_burst_count': post_burst_count,
        'avg_post_spam_score': avg_post_spam_score,
        # --- Upvote sent features ---
        'total_upvotes_sent': total_upvotes_sent,
        'unique_upvote_targets': unique_upvote_targets,
        'upvote_sent_burst_count': upvote_sent_burst_count,
        'mutual_upvote_count': mutual_upvote_count
    }
    return features

# For batch processing
def extract_features_batch(user_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [extract_features(log) for log in user_logs] 