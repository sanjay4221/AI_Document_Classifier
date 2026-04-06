from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db import crud
from backend.api.deps import get_current_user
from backend.classifier.hybrid import classify_document
from backend.core.logger import logger, audit_logger
from backend.core.limiter import limiter
from fastapi import Request
import os
from backend.core.config import settings

router = APIRouter(prefix="/classify", tags=["Classify"])


@router.post("/{document_id}")
@limiter.limit("20/minute")
async def classify(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch document
    doc = crud.get_document(db, document_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status == "classified":
        result = crud.get_classification(db, document_id)
        return _format_result(doc, result)

    # Run classification
    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    try:
        crud.update_document_status(db, document_id, "processing")
        result_data = await classify_document(file_path)

        # Save result
        result = crud.create_classification(
            db,
            document_id=document_id,
            department=result_data["department"],
            confidence_score=result_data["confidence_score"],
            explanation=result_data["explanation"],
            method_used=result_data["method_used"],
            raw_text_preview=result_data.get("text_preview", ""),
        )
        crud.update_document_status(db, document_id, "classified")

        audit_logger.info(
            f"CLASSIFIED | doc={document_id} | user={current_user.email} | "
            f"dept={result_data['department']} | score={result_data['confidence_score']:.2f} | "
            f"method={result_data['method_used']}"
        )
        return _format_result(doc, result)

    except Exception as e:
        crud.update_document_status(db, document_id, "failed")
        logger.error(f"Classification failed for doc {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/result")
async def get_result(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = crud.get_document(db, document_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    result = crud.get_classification(db, document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not yet classified")
    return _format_result(doc, result)


def _format_result(doc, result):
    return {
        "document_id": doc.id,
        "filename": doc.original_filename,
        "department": result.department,
        "confidence_score": round(result.confidence_score * 100, 1),
        "explanation": result.explanation,
        "method_used": result.method_used,
        "classified_at": result.created_at,
    }
