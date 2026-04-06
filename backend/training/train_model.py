"""
train_model.py — Train and Save the ML Classifier
Run this ONCE before starting the app to create the .pkl model files.

Usage:
    python -m backend.training.train_model

What it does:
1. Loads synthetic training data (72 labelled documents)
2. Splits into train/test sets
3. Builds TF-IDF vectorizer — converts text to numeric features
4. Trains Logistic Regression classifier
5. Evaluates accuracy and prints classification report
6. Saves model + vectorizer as .pkl files for runtime use
"""

import os
import sys
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.training.synthetic_data import get_training_samples, get_department_counts
from backend.core.config import settings


def train_and_save():
    print("\n🤖 AI Document Classifier — ML Model Training")
    print("=" * 55)

    # ── Step 1: Load training data ─────────────────────────────
    texts, labels = get_training_samples()
    print(f"\n📊 Training data loaded:")
    for dept, count in get_department_counts().items():
        print(f"   {dept}: {count} samples")
    print(f"   Total: {len(texts)} samples across {len(set(labels))} departments")

    # ── Step 2: Split train/test ──────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"\n📂 Split: {len(X_train)} train / {len(X_test)} test")

    # ── Step 3: Build TF-IDF Vectorizer ───────────────────────
    # ngram_range=(1,2) — captures single words AND word pairs
    # e.g. "invoice" AND "invoice number" both become features
    # max_features=5000 — top 5000 most informative words
    # min_df=1 — include words appearing in at least 1 doc
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        min_df=1,
        sublinear_tf=True,  # Apply log normalization to term freq
        strip_accents='unicode',
        analyzer='word',
        token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b',  # Only alphabetic words
    )

    # ── Step 4: Train Logistic Regression ─────────────────────
    # C=5 — moderate regularization (prevents overfitting)
    # max_iter=1000 — enough iterations to converge
    # multi_class='multinomial' — proper multi-class handling
    classifier = LogisticRegression(
        C=5,
        max_iter=1000,
        multi_class='multinomial',
        solver='lbfgs',
        random_state=42,
    )

    # ── Step 5: Fit and evaluate ──────────────────────────────
    print("\n⚙️  Training model...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    classifier.fit(X_train_vec, y_train)

    # Predictions
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n✅ Test Accuracy: {accuracy * 100:.1f}%")
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred))

    # Cross validation for more robust estimate
    print("🔄 Cross-validation (5-fold)...")
    X_all_vec = vectorizer.transform(texts)
    cv_scores = cross_val_score(classifier, X_all_vec, labels, cv=5)
    print(f"   CV Accuracy: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

    # ── Step 6: Save models ───────────────────────────────────
    os.makedirs(settings.MODEL_DIR, exist_ok=True)

    vectorizer_path = os.path.join(settings.MODEL_DIR, "tfidf_vectorizer.pkl")
    model_path = os.path.join(settings.MODEL_DIR, "logistic_model.pkl")

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(classifier, model_path)

    print(f"\n💾 Models saved:")
    print(f"   {vectorizer_path}")
    print(f"   {model_path}")

    # Show top features per department
    print("\n🔍 Top 5 keywords per department:")
    feature_names = vectorizer.get_feature_names_out()
    for i, dept in enumerate(classifier.classes_):
        top_indices = np.argsort(classifier.coef_[i])[-5:][::-1]
        top_words = [feature_names[j] for j in top_indices]
        print(f"   {dept}: {', '.join(top_words)}")

    print("\n🎉 Training complete! ML model ready for use.")
    return accuracy


if __name__ == "__main__":
    train_and_save()
