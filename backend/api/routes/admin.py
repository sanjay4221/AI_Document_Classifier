from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db import crud
from backend.api.deps import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def list_users(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    users = crud.get_all_users(db)
    return [{"id": u.id, "email": u.email, "full_name": u.full_name,
              "is_admin": u.is_admin, "is_active": u.is_active,
              "created_at": u.created_at} for u in users]


@router.get("/documents")
async def list_all_documents(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    docs = crud.get_all_documents(db)
    return [{"id": d.id, "user_id": d.user_id, "filename": d.original_filename,
              "status": d.status, "upload_time": d.upload_time} for d in docs]


@router.get("/classifications")
async def list_all_classifications(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    results = crud.get_all_classifications(db)
    return [{"id": r.id, "document_id": r.document_id, "department": r.department,
              "confidence_score": r.confidence_score, "method_used": r.method_used,
              "created_at": r.created_at} for r in results]


@router.get("/stats")
async def stats(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    users = crud.get_all_users(db)
    docs = crud.get_all_documents(db)
    results = crud.get_all_classifications(db)

    dept_counts = {}
    for r in results:
        dept_counts[r.department] = dept_counts.get(r.department, 0) + 1

    method_counts = {}
    for r in results:
        method_counts[r.method_used] = method_counts.get(r.method_used, 0) + 1

    return {
        "total_users": len(users),
        "total_documents": len(docs),
        "total_classified": len(results),
        "by_department": dept_counts,
        "by_method": method_counts,
        "avg_confidence": round(sum(r.confidence_score for r in results) / len(results) * 100, 1) if results else 0,
    }


@router.post("/users/{user_id}/make-admin")
async def make_admin(user_id: int, db: Session = Depends(get_db), _=Depends(get_admin_user)):
    user = crud.set_admin(db, user_id, True)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"{user.email} is now admin"}
