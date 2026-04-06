"""
ml_classifier.py — Scikit-learn ML Fallback Classifier
Loads the pre-trained TF-IDF + Logistic Regression model.

Why this exists:
- Groq API can be slow, hit rate limits, or return low confidence
- ML model is instant (no API call), always available
- Acts as safety net — ensures every document gets classified

Why TF-IDF + Logistic Regression?
- TF-IDF: converts text to numbers based on word importance
  (words that appear often in one category but rarely in others score high)
- Logistic Regression: fast, interpretable, works very well on text
- Together they're lightweight (~5MB) and run in milliseconds
"""

import os
import joblib
import numpy as np
from backend.core.config import settings
from backend.core.logger import logger
from backend.core.exceptions import ClassificationException

# Model file paths
VECTORIZER_PATH = os.path.join(settings.MODEL_DIR, "tfidf_vectorizer.pkl")
MODEL_PATH = os.path.join(settings.MODEL_DIR, "logistic_model.pkl")

# Lazy-loaded globals (loaded once on first use)
_vectorizer = None
_model = None


def _load_models():
    """Load saved models from disk. Called once, then cached."""
    global _vectorizer, _model

    if _vectorizer is not None and _model is not None:
        return  # Already loaded

    if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MODEL_PATH):
        raise ClassificationException(
            "ML models not found. Run: python -m backend.training.train_model"
        )

    _vectorizer = joblib.load(VECTORIZER_PATH)
    _model = joblib.load(MODEL_PATH)
    logger.info("ML models loaded from disk")


def classify_with_ml(text: str) -> dict:
    """
    Classify document text using the trained ML model.

    Returns dict with:
    - department: str (predicted class)
    - confidence: float (highest class probability)
    - explanation: str
    - all_scores: dict (confidence per department — useful for debugging)
    """
    _load_models()

    # Transform text to TF-IDF feature vector
    features = _vectorizer.transform([text])

    # Get prediction and probability scores for all classes
    prediction = _model.predict(features)[0]
    probabilities = _model.predict_proba(features)[0]
    class_labels = _model.classes_

    # Build confidence dict for all departments
    all_scores = {
        label: round(float(prob), 4)
        for label, prob in zip(class_labels, probabilities)
    }

    confidence = float(np.max(probabilities))

    explanation = (
        f"ML model (TF-IDF + Logistic Regression) classified this as {prediction} "
        f"with {confidence*100:.1f}% confidence based on document vocabulary patterns."
    )

    logger.info(f"ML classified as: {prediction} ({confidence:.2f})")

    return {
        "department": prediction,
        "confidence": confidence,
        "explanation": explanation,
        "all_scores": all_scores,
    }


def is_model_available() -> bool:
    """Check if trained model files exist."""
    return os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH)
