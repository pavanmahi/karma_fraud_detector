import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class RealisticUserGenerator:
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)

        self.normal_comments = [
            "Great discussion, thanks for posting!", "Insightful post, learned something new.",
            "Well explained.", "Nice analysis!", "Really enjoyed reading this!", "Good find!",
            "Appreciate the details!", "Thanks for the update.", "Helpful explanation.",
            "Clear and concise.", "Agreed.", "Interesting!", "Makes sense.", "This is helpful.",
            "Thanks!", "Nice!", "Fair point.", "True that."
        ]

        self.suspicious_comments = [
            "Insane", "Fire post!", "Unreal", "Mind blown!", "Crazy good!", "This hits, up!",
            "Epic, more pls!", "Legend post!", "Wild, upvote!", "Major W!", "Gold content!", "Hype this!",
            "Wow", "Viral vibes!", "Straight fire!", "Facts, up!", "This slaps!", "Banger post!",
            "Peak", "Truth, vote!", "King move!", "No cap, up!", "Lit content!", "Needed this, up!",
            "Quick", "Short and sweet!", "Up this now!", "Keep it up!", "Nice, again!"
        ]

        self.spam_comments = [
            "Upvote me now", "Check my page", "Pls upvote fast", "Boost this post",
            "Click my link", "Vote me up", "Sub for sub", "Need karma fast",
            "Karma farming", "Upvote exchange", "New here, need karma", "Follow back",
            "Drop an upvote!", "Karma needed ASAP!", "Link in bio!", "Upvote for upvote!",
            "Pls boost me!", "Check this out!", "Need votes now!", "Support my post!",
            "Follow me quick!", "Karma trade?", "Vote this up!", "Join my page!",
            "Upvote my stuff!", "Help me grow!", "Click here now!", "Karma plz!"
        ]

        # Add post content lists for each user type
        self.normal_posts = [
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
        self.suspicious_posts = [
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
        self.fraudulent_posts = [
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

    def _add_noise(self, text):
        if random.random() < 0.1:
            text = text.lower() if random.random() < 0.5 else text.upper()
        if random.random() < 0.05:
            if len(text) > 2:
                i = random.randint(1, len(text)-2)
                text = text[:i] + text[i+1] + text[i] + text[i+2:]
        if random.random() < 0.05:
            if random.random() < 0.5:
                text = text.replace(" ", "  ")
            else:
                text += text[-1]
        if random.random() < 0.2:
            text += random.choice(["!", "...", "🔥", "💯", "👍", "😊", "🚀", "😍", "👀"])
        return text

    def _generate_timestamps(self, base_time, user_type, num_acts):
        ts = []
        now = base_time
        for _ in range(num_acts):
            gap = np.random.exponential(scale={
                'normal': 72,
                'suspicious': 24,
                'fraudulent': 5
            }[user_type])
            now = now - timedelta(hours=gap)
            ts.append(now)
        return sorted(ts, reverse=True)

    def generate_user(self, user_type, user_id):
        base_time = datetime.now()
        user = {
            "user_id": user_id,
            "account_age_days": 0,
            "karma_log": [],
            "label": user_type
        }

        if user_type == 'normal':
            user["account_age_days"] = random.randint(15, 1000)
        elif user_type == 'suspicious':
            user["account_age_days"] = random.randint(3, 50)
        else:
            user["account_age_days"] = random.randint(1, 15)

        num_posts = random.randint(1, 2)
        num_comments = random.randint(2, 6)
        num_upvotes = random.randint(3, 7)
        total = num_posts + num_comments + num_upvotes
        timestamps = self._generate_timestamps(base_time, user_type, total)

        # --- Post Created ---
        posts = []
        for i in range(num_posts):
            if user_type == 'normal':
                post_content = self._add_noise(random.choice(self.normal_posts))
            elif user_type == 'suspicious':
                post_content = self._add_noise(random.choice(self.suspicious_posts))
            else:
                post_content = self._add_noise(random.choice(self.fraudulent_posts))
            posts.append(post_content)
            user["karma_log"].append({
                "activity_id": f"act_{user_type[0]}_{user_id}_p{i}",
                "type": "post_created",
                "content": post_content,
                "timestamp": timestamps[i].isoformat() + "Z"
            })

        # --- Comments ---
        comment_pool = []
        if user_type == 'normal':
            comment_pool = self.normal_comments + (self.suspicious_comments[:5] if random.random() < 0.3 else [])
        elif user_type == 'suspicious':
            bot_upvote_ratio = np.random.uniform(0.3, 0.8)
            comment_pool = self.suspicious_comments[:]
            if random.random() < 0.4:
                comment_pool += random.sample(self.normal_comments, 5)
            if random.random() < 0.3:
                comment_pool += random.sample(self.spam_comments, 3)
            base_comment = random.choice(comment_pool)
            comments = []
            for _ in range(num_comments):
                if random.random() < 0.3:
                    comments.append(self._add_noise(base_comment))
                else:
                    comments.append(self._add_noise(random.choice(comment_pool)))
        else:
            comment_pool = self.spam_comments + (self.suspicious_comments[:3] if random.random() < 0.2 else [])
            comments = [self._add_noise(random.choice(comment_pool)) for _ in range(num_comments)]
            bot_upvote_ratio = np.random.uniform(0.8, 1.2)
            burst_count = np.random.randint(1, 5)

        if user_type != 'suspicious':
            comments = [self._add_noise(random.choice(comment_pool)) for _ in range(num_comments)]

        if user_type == 'normal' and random.random() < 0.1:
            comments[0] = random.choice(self.spam_comments)
        if user_type == 'fraudulent' and random.random() < 0.2:
            comments[0] = random.choice(self.normal_comments)

        for i, content in enumerate(comments):
            user["karma_log"].append({
                "activity_id": f"act_{user_type[0]}_{user_id}_c{i}",
                "type": "comment",
                "content": content,
                "timestamp": timestamps[num_posts + i].isoformat() + "Z"
            })

        # --- Upvotes (Received & Sent) ---
        for i in range(num_upvotes):
            upvote_timestamp = timestamps[num_posts + num_comments + i].isoformat() + "Z"
            if user_type == 'normal':
                from_user_age = random.randint(30, 500)
                from_user = f"usr_{random.randint(1000,9999)}"
                # Upvote received
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_u{i}",
                    "type": "upvote_received",
                    "from_user": from_user,
                    "from_user_age_days": from_user_age,
                    "timestamp": upvote_timestamp
                })
                # Upvote sent (to a random user)
                sent_to_user = f"usr_{random.randint(1000,9999)}"
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_us{i}",
                    "type": "upvote_sent",
                    "to_user": sent_to_user,
                    "to_user_age_days": random.randint(10, 1000),
                    "timestamp": upvote_timestamp
                })
            elif user_type == 'suspicious':
                from_user_age = random.choices(
                    [random.randint(2, 5), random.randint(30, 100)],
                    weights=[0.6, 0.4],
                    k=1
                )[0]
                from_user = f"usr_{random.randint(1000,9999)}"
                # Upvote received
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_u{i}",
                    "type": "upvote_received",
                    "from_user": from_user,
                    "from_user_age_days": from_user_age,
                    "timestamp": upvote_timestamp
                })
                # Upvote sent (to a random user)
                sent_to_user = f"usr_{random.randint(1000,9999)}"
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_us{i}",
                    "type": "upvote_sent",
                    "to_user": sent_to_user,
                    "to_user_age_days": random.randint(2, 100),
                    "timestamp": upvote_timestamp
                })
            else:  # fraudulent
                # For fraudulent, mutual upvotes: upvote_received and upvote_sent to the same user, but with slightly different timestamps
                mutual_user = f"usr_{random.randint(1000,9999)}"
                mutual_user_age = random.randint(1, 10)
                # Generate two close but not identical timestamps
                base_upvote_time = timestamps[num_posts + num_comments + i]
                offset_minutes = random.randint(1, 60)
                if random.random() < 0.5:
                    sent_time = base_upvote_time + timedelta(minutes=offset_minutes)
                    received_time = base_upvote_time
                else:
                    sent_time = base_upvote_time
                    received_time = base_upvote_time + timedelta(minutes=offset_minutes)
                # Upvote received
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_u{i}",
                    "type": "upvote_received",
                    "from_user": mutual_user,
                    "from_user_age_days": mutual_user_age,
                    "timestamp": received_time.isoformat() + "Z"
                })
                # Upvote sent (to the same user)
                user["karma_log"].append({
                    "activity_id": f"act_{user_type[0]}_{user_id}_us{i}",
                    "type": "upvote_sent",
                    "to_user": mutual_user,
                    "to_user_age_days": mutual_user_age,
                    "timestamp": sent_time.isoformat() + "Z"
                })

        return user

    def generate_dataset(self, n_normals, n_suspicious, n_fraud, flip_ratio=0.05):
        dataset = []
        for i in range(n_normals):
            dataset.append(self.generate_user("normal", f"normal_{i+1:04}"))
        for i in range(n_suspicious):
            dataset.append(self.generate_user("suspicious", f"suspicious_{i+1:04}"))
        for i in range(n_fraud):
            dataset.append(self.generate_user("fraudulent", f"fraudulent_{i+1:04}"))

        total = len(dataset)
        flip_count = int(total * flip_ratio)
        flip_targets = random.sample(dataset, flip_count)
        for user in flip_targets:
            original = user["label"]
            choices = ["normal", "suspicious", "fraudulent"]
            choices.remove(original)
            user["label"] = random.choice(choices)

        random.shuffle(dataset)
        return dataset

def add_noise_to_label(label, noise_level=0.15):
    if random.random() < noise_level:
        choices = ['normal', 'suspicious', 'fraudulent']
        choices.remove(label)
        return random.choice(choices)
    return label

def generate_realistic_hard_dataset(n_normals, n_suspicious, n_fraud, flip_ratio=0.10, overlap_ratio=0.25):
    generator = RealisticUserGenerator(seed=42)
    dataset = []
    for i in range(n_normals):
        user = generator.generate_user('normal', f'normal_{i+1:04}')
        user['account_age_days'] = random.randint(15, 1000)
        if random.random() < overlap_ratio:
            user['karma_log'][0]['content'] = random.choice(generator.spam_comments + generator.suspicious_comments)
        user['label'] = add_noise_to_label(user['label'], noise_level=flip_ratio)
        dataset.append(user)
    for i in range(n_suspicious):
        user = generator.generate_user('suspicious', f'suspicious_{i+1:04}')
        if random.random() < 0.15:
            user['account_age_days'] = random.randint(1, 15)
        else:
            user['account_age_days'] = random.randint(15, 1000)
        if random.random() < overlap_ratio:
            user['karma_log'][0]['content'] = random.choice(generator.normal_comments)
        user['label'] = add_noise_to_label(user['label'], noise_level=flip_ratio)
        dataset.append(user)
    for i in range(n_fraud):
        user = generator.generate_user('fraudulent', f'fraudulent_{i+1:04}')
        if random.random() < 0.15:
            user['account_age_days'] = random.randint(1, 15)
        else:
            user['account_age_days'] = random.randint(15, 1000)
        if random.random() < overlap_ratio:
            user['karma_log'][0]['content'] = random.choice(generator.normal_comments + generator.suspicious_comments)
        user['label'] = add_noise_to_label(user['label'], noise_level=flip_ratio)
        dataset.append(user)
    random.shuffle(dataset)
    return dataset

def main():
    os.makedirs("data", exist_ok=True)
    print('Generating optimal training set...')
    train_optimal = generate_realistic_hard_dataset(400, 240, 160, flip_ratio=0.10, overlap_ratio=0.25)
    print('Generating optimal test set...')
    test_optimal = generate_realistic_hard_dataset(100, 60, 40, flip_ratio=0.10, overlap_ratio=0.25)
    with open('data/optimal_train.json', 'w') as f:
        json.dump(train_optimal, f, indent=2)
    with open('data/optimal_test.json', 'w') as f:
        json.dump(test_optimal, f, indent=2)
    print('✅ Done! Optimal Training:', len(train_optimal), 'Test:', len(test_optimal))

if __name__ == "__main__":
    main() 