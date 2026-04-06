from sqlalchemy.orm import Session
from typing import Optional, List
from backend.db.models import User, Document, ClassificationResult
from backend.core.security import hash_password


# ── Users ────────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, password: str, full_name: str) -> User:
    user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()

def set_admin(db: Session, user_id: int, is_admin: bool) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if user:
        user.is_admin = is_admin
        db.commit()
        db.refresh(user)
    return user


# ── Documents ─────────────────────────────────────────────────
def create_document(db: Session, user_id: int, filename: str,
                    original_filename: str, file_size: int) -> Document:
    doc = Document(user_id=user_id, filename=filename,
                   original_filename=original_filename, file_size=file_size)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db: Session, doc_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == doc_id).first()

def get_user_documents(db: Session, user_id: int) -> List[Document]:
    return db.query(Document).filter(Document.user_id == user_id).order_by(Document.upload_time.desc()).all()

def update_document_status(db: Session, doc_id: int, status: str) -> None:
    doc = get_document(db, doc_id)
    if doc:
        doc.status = status
        db.commit()

def get_all_documents(db: Session) -> List[Document]:
    return db.query(Document).order_by(Document.upload_time.desc()).all()

def delete_document(db: Session, doc_id: int) -> bool:
    """
    Delete document record + its classification result from DB.
    File on disk is kept (as per requirement).
    Returns True if deleted, False if not found.
    """
    doc = get_document(db, doc_id)
    if not doc:
        return False
    # Delete classification first (FK constraint)
    result = db.query(ClassificationResult).filter(
        ClassificationResult.document_id == doc_id
    ).first()
    if result:
        db.delete(result)
    db.delete(doc)
    db.commit()
    return True

def reset_classification(db: Session, doc_id: int) -> bool:
    """
    Delete classification result only — keeps document record.
    Resets status to pending so it can be reclassified.
    """
    result = db.query(ClassificationResult).filter(
        ClassificationResult.document_id == doc_id
    ).first()
    if result:
        db.delete(result)
    doc = get_document(db, doc_id)
    if doc:
        doc.status = "pending"
    db.commit()
    return True


# ── Classification Results ─────────────────────────────────────
def create_classification(db: Session, document_id: int, department: str,
                           confidence_score: float, explanation: str,
                           method_used: str, raw_text_preview: str = "") -> ClassificationResult:
    result = ClassificationResult(
        document_id=document_id,
        department=department,
        confidence_score=confidence_score,
        explanation=explanation,
        method_used=method_used,
        raw_text_preview=raw_text_preview[:500],
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

def get_classification(db: Session, doc_id: int) -> Optional[ClassificationResult]:
    return db.query(ClassificationResult).filter(
        ClassificationResult.document_id == doc_id
    ).first()

def get_all_classifications(db: Session) -> List[ClassificationResult]:
    return db.query(ClassificationResult).order_by(ClassificationResult.created_at.desc()).all()