from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)  # bytes
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending / classified / failed

    owner = relationship("User", back_populates="documents")
    classification = relationship("ClassificationResult", back_populates="document", uselist=False)


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    department = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    method_used = Column(String, nullable=False)  # llm / ml / hybrid
    raw_text_preview = Column(Text)  # first 500 chars for audit
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="classification")
