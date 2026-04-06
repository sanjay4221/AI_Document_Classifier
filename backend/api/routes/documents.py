import os, uuid, shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db import crud
from backend.api.deps import get_current_user
from backend.core.config import settings
from backend.core.logger import logger
from backend.core.exceptions import InvalidFileTypeException, FileTooLargeException
from backend.core.limiter import limiter
from fastapi import Request

router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", status_code=201)
@limiter.limit("10/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validate type
    if not file.filename.lower().endswith(".pdf"):
        raise InvalidFileTypeException()

    contents = await file.read()

    # Validate size
    if len(contents) > MAX_BYTES:
        raise FileTooLargeException(settings.MAX_FILE_SIZE_MB)

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Save to DB
    doc = crud.create_document(
        db,
        user_id=current_user.id,
        filename=safe_name,
        original_filename=file.filename,
        file_size=len(contents),
    )
    logger.info(f"Document uploaded: {file.filename} by user {current_user.email}")
    return {"document_id": doc.id, "filename": file.filename, "status": doc.status}


@router.get("/")
async def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs = crud.get_user_documents(db, current_user.id)
    return [
        {
            "id": d.id,
            "filename": d.original_filename,
            "file_size": d.file_size,
            "status": d.status,
            "upload_time": d.upload_time,
            "classification": {
                "department": d.classification.department,
                "confidence_score": d.classification.confidence_score,
                "method_used": d.classification.method_used,
            } if d.classification else None,
        }
        for d in docs
    ]


@router.delete("/{document_id}", status_code=200)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete document DB record + classification result.
    File on disk is kept. Owner only.
    """
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your document")

    crud.delete_document(db, document_id)
    logger.info(f"Document {document_id} deleted by {current_user.email}")
    return {"message": f"Document {document_id} deleted"}


@router.post("/{document_id}/reclassify", status_code=200)
@limiter.limit("10/minute")
async def reclassify_document(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Reset existing classification and re-run full pipeline.
    Useful when result had low confidence or model has been retrained.
    """
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your document")

    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original file no longer on disk")

    # Wipe old result + reset status
    crud.reset_classification(db, document_id)
    logger.info(f"Document {document_id} reset for reclassification by {current_user.email}")

    from backend.classifier.hybrid import classify_document
    try:
        crud.update_document_status(db, document_id, "processing")
        result_data = await classify_document(file_path)

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

        logger.info(
            f"Reclassified doc {document_id} → {result_data['department']} "
            f"({result_data['confidence_score']:.2f}) via {result_data['method_used']}"
        )
        return {
            "document_id": document_id,
            "filename": doc.original_filename,
            "department": result.department,
            "confidence_score": round(result.confidence_score * 100, 1),
            "explanation": result.explanation,
            "method_used": result.method_used,
            "classified_at": result.created_at,
        }
    except Exception as e:
        crud.update_document_status(db, document_id, "failed")
        logger.error(f"Reclassification failed for doc {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))