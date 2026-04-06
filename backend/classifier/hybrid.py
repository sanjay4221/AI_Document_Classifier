"""
hybrid.py — The Decision Engine (ML-First, Cost Optimised)
Orchestrates the full classification pipeline.

Cost Optimised Strategy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PDF → extract → preprocess
          ↓
  Step 1: Run ML classifier (FREE, instant, no API)
          ↓
  ML confidence >= ML_THRESHOLD (0.82)?
  YES → return ML result ✅ (Groq API never called = cost saved)
  NO  → Step 2: Call Groq LLM for accuracy
          ↓
  Both results available — ensemble decision:
    • Both agree    → boost confidence (method: hybrid)
    • LLM wins      → use LLM (method: llm)
    • ML still wins → use ML  (method: ml)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Why ML-first?
- ML is instant (milliseconds), runs locally, zero API cost
- Routine clear documents (invoices, SOPs, contracts) score
  very high confidence → LLM never needed
- Only ambiguous/complex docs escalate to LLM
- Expected LLM call reduction: ~60-70% at scale
"""

from backend.classifier.extractor import extract_text_from_pdf
from backend.classifier.preprocessor import (
    preprocess_text,
    preprocess_text_for_llm,
    get_text_preview,
    is_text_sufficient,
)
from backend.classifier.groq_classifier import classify_with_groq
from backend.classifier.ml_classifier import classify_with_ml, is_model_available
from backend.core.config import settings
from backend.core.logger import logger, audit_logger
from backend.core.exceptions import ClassificationException


# ── Thresholds ─────────────────────────────────────────────────
# ML confidence needed to skip LLM entirely (cost save trigger)
ML_CONFIDENCE_THRESHOLD = 0.82  # Tuned on validation set to balance cost vs accuracy

# LLM confidence needed to prefer LLM over ML when both run
LLM_CONFIDENCE_THRESHOLD = settings.LLM_CONFIDENCE_THRESHOLD  # 0.75


async def classify_document(file_path: str) -> dict:
    """
    Full ML-first classification pipeline for a PDF file.

    Returns:
    {
        "department":       "Finance",
        "confidence_score": 0.94,
        "explanation":      "...",
        "method_used":      "ml",       # ml / llm / hybrid
        "text_preview":     "...",
        "llm_called":       False,      # audit: did we call Groq?
        "llm_result":       None,
        "ml_result":        {...},
    }
    """
    import os
    logger.info(f"▶ Classification pipeline started: {os.path.basename(file_path)}")

    # ── Step 1: Extract text ───────────────────────────────────
    raw_text = extract_text_from_pdf(file_path)

    if not is_text_sufficient(raw_text):
        raise ClassificationException(
            "Document has insufficient text. It may be a scanned image PDF."
        )

    text_preview = get_text_preview(raw_text)

    # ── Step 2: ML Classification (always runs first — FREE) ───
    ml_result = None
    ml_confidence = 0.0

    if not is_model_available():
        logger.warning("ML model not found — skipping to LLM directly")
        logger.warning("Run: python -m backend.training.train_model")
    else:
        # ML uses shorter text (800 chars) — fast and sufficient
        ml_text = preprocess_text(raw_text, max_chars=800)
        ml_result = classify_with_ml(ml_text)
        ml_confidence = ml_result["confidence"]
        logger.info(
            f"  ML → {ml_result['department']} @ {ml_confidence:.2f} "
            f"(threshold: {ML_CONFIDENCE_THRESHOLD})"
        )

    # ── Step 3: Cost Decision Gate ─────────────────────────────
    llm_called  = False
    llm_result  = None
    llm_confidence = 0.0

    if ml_confidence >= ML_CONFIDENCE_THRESHOLD:
        # ✅ ML confident enough — skip LLM entirely
        logger.info(
            f"  ✅ ML confidence {ml_confidence:.2f} >= {ML_CONFIDENCE_THRESHOLD} "
            f"— LLM skipped (cost saved)"
        )
        final   = ml_result
        method  = "ml"

    else:
        # ⚡ ML not confident — escalate to Groq LLM
        logger.info(
            f"  ⚡ ML confidence {ml_confidence:.2f} < {ML_CONFIDENCE_THRESHOLD} "
            f"— escalating to Groq LLM"
        )
        llm_called = True

        try:
            # LLM gets more context (2000 chars) for harder cases
            llm_text   = preprocess_text_for_llm(raw_text, max_chars=2000)
            llm_result = await classify_with_groq(llm_text)
            llm_confidence = llm_result["confidence"]
            logger.info(f"  LLM → {llm_result['department']} @ {llm_confidence:.2f}")

        except Exception as e:
            logger.error(f"  LLM failed: {e}")
            # LLM failed — fall back to ML result even if low confidence
            if ml_result:
                logger.warning("  Using ML result despite low confidence (LLM unavailable)")
                final  = ml_result
                method = "ml"
                _log_result(final, method, llm_called, file_path)
                return _build_response(final, method, text_preview, llm_called, llm_result, ml_result)
            raise ClassificationException(f"Both ML and LLM failed: {e}")

        # ── Step 4: Ensemble Decision (both results available) ──
        final, method = _ensemble_decision(ml_result, llm_result, ml_confidence, llm_confidence)

    # ── Step 5: Build and return response ─────────────────────
    _log_result(final, method, llm_called, file_path)
    return _build_response(final, method, text_preview, llm_called, llm_result, ml_result)


def _ensemble_decision(ml_result, llm_result, ml_conf, llm_conf):
    """
    Smart ensemble when both ML and LLM have run.

    Rules:
    1. Both agree on department → boost confidence, method=hybrid
    2. LLM confidence >= threshold → trust LLM, method=llm
    3. ML confidence > LLM confidence → trust ML, method=ml
    4. Tiebreak → prefer LLM (richer explanation)
    """
    ml_dept  = ml_result["department"]
    llm_dept = llm_result["department"]

    if ml_dept == llm_dept:
        # Agreement — average + small boost
        boosted = min(1.0, (ml_conf + llm_conf) / 2 + 0.05)
        logger.info(
            f"  🤝 Ensemble AGREE: {ml_dept} | "
            f"ML={ml_conf:.2f} LLM={llm_conf:.2f} → boosted={boosted:.2f}"
        )
        return {
            "department":  ml_dept,
            "confidence":  boosted,
            "explanation": (
                f"Both AI models agreed: {ml_dept}. "
                f"{llm_result['explanation']}"
            ),
        }, "hybrid"

    elif llm_conf >= LLM_CONFIDENCE_THRESHOLD:
        logger.info(
            f"  🏆 LLM wins: {llm_dept} ({llm_conf:.2f}) "
            f"over ML: {ml_dept} ({ml_conf:.2f})"
        )
        return llm_result, "llm"

    elif ml_conf > llm_conf:
        logger.info(
            f"  🏆 ML wins: {ml_dept} ({ml_conf:.2f}) "
            f"over LLM: {llm_dept} ({llm_conf:.2f})"
        )
        return ml_result, "ml"

    else:
        # Tiebreak — LLM has better explanation
        logger.info(f"  Tiebreak → LLM preferred for explanation quality")
        return llm_result, "llm"


def _build_response(final, method, text_preview, llm_called, llm_result, ml_result):
    return {
        "department":       final["department"],
        "confidence_score": final["confidence"],
        "explanation":      final["explanation"],
        "method_used":      method,
        "text_preview":     text_preview,
        "llm_called":       llm_called,
        "llm_result":       llm_result,
        "ml_result":        ml_result,
    }


def _log_result(final, method, llm_called, file_path):
    import os
    cost_tag = "💰 API_SAVED" if not llm_called else "⚡ API_USED"
    audit_logger.info(
        f"{cost_tag} | file={os.path.basename(file_path)} | "
        f"dept={final['department']} | "
        f"score={final['confidence']:.2f} | "
        f"method={method} | "
        f"llm_called={llm_called}"
    )