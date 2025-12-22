from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ErrorCategory(Base):
    __tablename__ = "error_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(50), unique=True, index=True)
    category_name = Column(String(100))
    description = Column(Text, nullable=True)
    
    error_types = relationship("ErrorType", back_populates="category")
    questions = relationship("Question", back_populates="category")

class ErrorType(Base):
    __tablename__ = "error_types"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("error_categories.id"))
    error_type = Column(String(200))
    description = Column(Text, nullable=True)
    
    category = relationship("ErrorCategory", back_populates="error_types")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("error_categories.id"))
    question_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("ErrorCategory", back_populates="questions")
    results = relationship("AIResult", back_populates="question")

class AIResult(Base):
    __tablename__ = "ai_results"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    model_name = Column(String(100))
    model_provider = Column(String(50))  # gemini, huggingface
    response = Column(Text)
    response_time = Column(Float)  # seconds
    tested_at = Column(DateTime, default=datetime.utcnow)
    
    question = relationship("Question", back_populates="results")
