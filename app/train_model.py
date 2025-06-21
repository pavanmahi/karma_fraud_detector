import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix, classification_report
from joblib import dump
from app.feature_extractor import extract_features_batch
from sklearn.model_selection import cross_val_score

TRAIN_PATH = 'data/optimal_train.json'
TEST_PATH = 'data/optimal_test.json'
MODEL_PATH = 'model/model.pkl'
FEATURE_NAMES_PATH = 'model/feature_names.json'

LABEL_MAP = {'normal': 0, 'suspicious': 1, 'fraudulent': 2}

# Utility to extract X, y from dataset
def prepare_data(dataset):
    X_dicts = extract_features_batch(dataset)
    feature_names = [k for k in X_dicts[0] if k != 'user_id']
    X = np.array([[row[f] for f in feature_names] for row in X_dicts])
    y = np.array([LABEL_MAP.get(row.get('label', 'normal'), 0) for row in dataset])
    return X, y, feature_names

def main():
    os.makedirs('model', exist_ok=True)
    # Load data
    with open(TRAIN_PATH) as f:
        train_data = json.load(f)
    with open(TEST_PATH) as f:
        test_data = json.load(f)

    # Prepare features and labels
    X_train, y_train, feature_names = prepare_data(train_data)
    X_test, y_test, _ = prepare_data(test_data)

    print('\nFeatures used for training:')
    for fname in feature_names:
        print(' -', fname)

    # Train model
    clf = RandomForestClassifier(
        n_estimators=50,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=42,
        class_weight='balanced'
        )
    

    scores = cross_val_score(clf, X_train, y_train, cv=5, scoring='f1_weighted')
    print('Cross-validated F1 scores:', scores)
    print('Mean CV F1:', scores.mean())
    
    clf.fit(X_train, y_train)

    # Save model and feature names
    dump(clf, MODEL_PATH)
    with open(FEATURE_NAMES_PATH, 'w') as f:
        json.dump(feature_names, f)

    # Evaluate
    def print_metrics(X, y, split):
        y_pred = clf.predict(X)
        y_prob = clf.predict_proba(X)
        print(f'\n=== {split.upper()} METRICS ===')
        print('F1 Score:', f1_score(y, y_pred, average='weighted'))
        try:
            print('ROC AUC:', roc_auc_score(y, y_prob, multi_class='ovr'))
        except Exception as e:
            print('ROC AUC: Not available (', e, ')')
        print('Confusion Matrix:\n', confusion_matrix(y, y_pred))
        print('Classification Report:\n', classification_report(y, y_pred, target_names=list(LABEL_MAP.keys())))

    print_metrics(X_train, y_train, 'train')
    print_metrics(X_test, y_test, 'test')

    # Feature importance
    print('\n=== FEATURE IMPORTANCE ===')
    for name, score in sorted(zip(feature_names, clf.feature_importances_), key=lambda x: -x[1]):
        print(f'{name:30s}: {score:.4f}')

    print(f'\nModel saved to {MODEL_PATH}')
    print(f'Feature names saved to {FEATURE_NAMES_PATH}')

if __name__ == '__main__':
    main() 