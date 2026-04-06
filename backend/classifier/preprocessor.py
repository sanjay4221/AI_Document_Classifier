"""
preprocessor.py — Text Cleaning & Normalisation
Two preprocessing modes for cost optimisation:

  preprocess_text()        → 800 chars  — for ML classifier (fast, free)
  preprocess_text_for_llm() → 2000 chars — for LLM only when needed

Why different lengths?
- ML (TF-IDF): needs key vocabulary only — first 800 chars is plenty
  Most documents have their type/purpose in the first paragraph
- LLM: benefits from more context for edge cases — but still capped
  at 2000 (not 4000) to reduce token cost by 50% vs before
- Previous: always sent 4000 chars to LLM
- Now:      ML gets 800, LLM only called for hard cases gets 2000
- Token savings: ~75% reduction overall
"""

import re
import unicodedata
from backend.core.logger import logger


def _clean(raw_text: str) -> str:
    """
    Core cleaning pipeline — applied before any truncation.
    1. Unicode normalise
    2. Remove page markers
    3. Remove URLs + emails
    4. Remove excessive special chars
    5. Collapse whitespace
    """
    if not raw_text:
        return ""

    text = unicodedata.normalize("NFKC", raw_text)
    text = re.sub(r'\[Page \d+\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)
    text = re.sub(r'[^\w\s\.,;:!?\-\(\)\/\&\%\$\#\@\']', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def preprocess_text(raw_text: str, max_chars: int = 800) -> str:
    """
    ML preprocessing — short, fast, free.
    Default 800 chars captures document type/purpose always
    in the opening section which is all TF-IDF needs.
    """
    text = _clean(raw_text)

    if len(text) > max_chars:
        text = text[:max_chars]
        logger.debug(f"ML text truncated to {max_chars} chars")

    logger.debug(f"ML preprocessed: {len(raw_text)} → {len(text)} chars")
    return text


def preprocess_text_for_llm(raw_text: str, max_chars: int = 2000) -> str:
    """
    LLM preprocessing — more context for harder cases.
    Only called when ML confidence is below threshold.
    2000 chars (not 4000) = 50% token cost reduction vs before.

    Strategy: take first 1500 chars + last 500 chars
    This captures: document header/title + conclusion/signature
    Both are highly informative for classification.
    """
    text = _clean(raw_text)

    if len(text) <= max_chars:
        logger.debug(f"LLM text: {len(text)} chars (no truncation needed)")
        return text

    # Smart truncation: first 75% + last 25%
    first_part = int(max_chars * 0.75)   # 1500 chars from start
    last_part  = int(max_chars * 0.25)   # 500 chars from end

    combined = text[:first_part] + "\n...\n" + text[-last_part:]
    logger.debug(
        f"LLM text: {len(raw_text)} → {len(combined)} chars "
        f"(first {first_part} + last {last_part})"
    )
    return combined


def get_text_preview(raw_text: str, chars: int = 500) -> str:
    """Short preview for audit logging — first 500 chars."""
    return _clean(raw_text)[:chars]


def is_text_sufficient(text: str, min_chars: int = 100) -> bool:
    """
    Check if we have enough text to classify.
    Below 100 chars = likely a scanned/image PDF with no extractable text.
    """
    return len(text.strip()) >= min_chars