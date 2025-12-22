from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db, init_db
from models import ErrorCategory, ErrorType, Question, AIResult
from ai_services import (
    get_all_models, 
    test_question_with_model, 
    test_question_with_all_models,
    GEMINI_MODELS,
    HUGGINGFACE_MODELS
)

app = FastAPI(title="Hata Türleri AI Test Sistemi")

# Static dosyaları serve et
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic modelleri
class QuestionCreate(BaseModel):
    category_id: int
    question_text: str

class TestRequest(BaseModel):
    question_id: int
    model_name: str
    provider: str

class TestAllRequest(BaseModel):
    question_id: int

# Ana sayfa
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Veritabanını başlat
@app.on_event("startup")
async def startup():
    init_db()

# ==================== KATEGORI ENDPOINTLERI ====================

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """Tüm hata kategorilerini getirir"""
    categories = db.query(ErrorCategory).all()
    return [{
        "id": c.id,
        "category_code": c.category_code,
        "category_name": c.category_name,
        "description": c.description,
        "error_count": len(c.error_types),
        "question_count": len(c.questions)
    } for c in categories]

@app.get("/api/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Belirli bir kategorinin detaylarını getirir"""
    category = db.query(ErrorCategory).filter(ErrorCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    return {
        "id": category.id,
        "category_code": category.category_code,
        "category_name": category.category_name,
        "description": category.description,
        "error_types": [{
            "id": e.id,
            "error_type": e.error_type,
            "description": e.description
        } for e in category.error_types]
    }

# ==================== SORU ENDPOINTLERI ====================

@app.get("/api/questions")
def get_questions(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Tüm soruları veya kategori bazlı soruları getirir"""
    query = db.query(Question)
    if category_id:
        query = query.filter(Question.category_id == category_id)
    
    questions = query.order_by(Question.created_at.desc()).all()
    return [{
        "id": q.id,
        "category_id": q.category_id,
        "category_name": q.category.category_name if q.category else None,
        "category_code": q.category.category_code if q.category else None,
        "question_text": q.question_text,
        "created_at": q.created_at.isoformat(),
        "result_count": len(q.results)
    } for q in questions]

@app.post("/api/questions")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Yeni soru ekler"""
    category = db.query(ErrorCategory).filter(ErrorCategory.id == question.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    new_question = Question(
        category_id=question.category_id,
        question_text=question.question_text
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return {
        "id": new_question.id,
        "category_id": new_question.category_id,
        "question_text": new_question.question_text,
        "created_at": new_question.created_at.isoformat()
    }

@app.delete("/api/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Soru siler"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    
    # Önce sonuçları sil
    db.query(AIResult).filter(AIResult.question_id == question_id).delete()
    db.delete(question)
    db.commit()
    
    return {"message": "Soru silindi"}

# ==================== MODEL ENDPOINTLERI ====================

@app.get("/api/models")
def get_models():
    """Kullanılabilir tüm modelleri getirir"""
    return {
        "gemini": GEMINI_MODELS,
        "huggingface": HUGGINGFACE_MODELS,
        "all": get_all_models()
    }

# ==================== TEST ENDPOINTLERI ====================

@app.post("/api/test")
def test_with_model(request: TestRequest, db: Session = Depends(get_db)):
    """Bir soruyu belirli bir model ile test eder"""
    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    
    # Model ile test et
    result = test_question_with_model(
        question.question_text,
        request.model_name,
        request.provider
    )
    
    # Sonucu kaydet
    if result["success"]:
        ai_result = AIResult(
            question_id=question.id,
            model_name=request.model_name,
            model_provider=request.provider,
            response=result["response"],
            response_time=result["response_time"]
        )
        db.add(ai_result)
        db.commit()
        db.refresh(ai_result)
        
        return {
            "success": True,
            "result_id": ai_result.id,
            "model_name": request.model_name,
            "provider": request.provider,
            "response": result["response"],
            "response_time": result["response_time"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Unknown error"),
            "model_name": request.model_name,
            "provider": request.provider
        }

@app.post("/api/test-all")
def test_with_all_models(request: TestAllRequest, db: Session = Depends(get_db)):
    """Bir soruyu tüm modellerle test eder"""
    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    
    results = test_question_with_all_models(question.question_text)
    saved_results = []
    
    for result in results:
        if result["success"]:
            ai_result = AIResult(
                question_id=question.id,
                model_name=result["model_name"],
                model_provider=result["provider"],
                response=result["response"],
                response_time=result["response_time"]
            )
            db.add(ai_result)
            db.flush()
            
            saved_results.append({
                "success": True,
                "result_id": ai_result.id,
                "model_name": result["model_name"],
                "provider": result["provider"],
                "response": result["response"],
                "response_time": result["response_time"]
            })
        else:
            saved_results.append({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "model_name": result["model_name"],
                "provider": result["provider"]
            })
    
    db.commit()
    return {"results": saved_results}

# ==================== SONUÇ ENDPOINTLERI ====================

@app.get("/api/results")
def get_results(question_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Tüm test sonuçlarını veya soru bazlı sonuçları getirir"""
    query = db.query(AIResult)
    if question_id:
        query = query.filter(AIResult.question_id == question_id)
    
    results = query.order_by(AIResult.tested_at.desc()).all()
    return [{
        "id": r.id,
        "question_id": r.question_id,
        "question_text": r.question.question_text if r.question else None,
        "model_name": r.model_name,
        "model_provider": r.model_provider,
        "response": r.response,
        "response_time": r.response_time,
        "tested_at": r.tested_at.isoformat()
    } for r in results]

@app.get("/api/results/compare/{question_id}")
def compare_results(question_id: int, db: Session = Depends(get_db)):
    """Bir soru için tüm model sonuçlarını karşılaştırır"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    
    results = db.query(AIResult).filter(AIResult.question_id == question_id).all()
    
    return {
        "question": {
            "id": question.id,
            "text": question.question_text,
            "category": question.category.category_name if question.category else None
        },
        "results": [{
            "id": r.id,
            "model_name": r.model_name,
            "provider": r.model_provider,
            "response": r.response,
            "response_time": r.response_time,
            "tested_at": r.tested_at.isoformat()
        } for r in results]
    }

@app.delete("/api/results/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    """Sonuç siler"""
    result = db.query(AIResult).filter(AIResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Sonuç bulunamadı")
    
    db.delete(result)
    db.commit()
    
    return {"message": "Sonuç silindi"}

# ==================== İSTATİSTİK ENDPOINTLERI ====================

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Genel istatistikleri getirir"""
    total_categories = db.query(ErrorCategory).count()
    total_questions = db.query(Question).count()
    total_results = db.query(AIResult).count()
    
    # Model bazlı istatistikler
    from sqlalchemy import func
    model_stats = db.query(
        AIResult.model_name,
        AIResult.model_provider,
        func.count(AIResult.id).label('count'),
        func.avg(AIResult.response_time).label('avg_time')
    ).group_by(AIResult.model_name, AIResult.model_provider).all()
    
    return {
        "total_categories": total_categories,
        "total_questions": total_questions,
        "total_results": total_results,
        "model_stats": [{
            "model_name": s.model_name,
            "provider": s.model_provider,
            "test_count": s.count,
            "avg_response_time": round(s.avg_time, 2) if s.avg_time else 0
        } for s in model_stats]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
