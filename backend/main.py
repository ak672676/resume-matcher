import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import uuid
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from retrain_cron import retrain_model
import pickle
from fastapi.middleware.cors import CORSMiddleware


# 🔁 Import real model logic
from model_utils import predict_role_from_skills, predict_role_with_confidence
from skill_extractor import skill_extractor

# Load env variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("Loaded DATABASE_URL:", DATABASE_URL)

# Create FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# ---------- Connectivity Check at Startup ----------
@app.on_event("startup")
def test_database_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully.")
    except OperationalError as e:
        print("❌ Database connection failed.")
        print(e)
        raise RuntimeError("Failed to connect to the database.") from e
# ---------------------------------------------------

# Intelligent skill extraction using the SkillExtractor class
def extract_skills(text: str) -> List[str]:
    """
    Extract skills from resume text using intelligent pattern matching
    """
    return skill_extractor.extract_skills(text)

# Input schema
class ResumeInput(BaseModel):
    user_email: str
    resume_text: str
    
class PredictRequest(BaseModel):
    skills: List[str]

class ConfirmRoleRequest(BaseModel):
    resume_id: str
    confirmed_role: str


# Main API route
@app.post("/analyze")
def analyze_resume(payload: ResumeInput):
    skills = extract_skills(payload.resume_text)
    
    # ✅ Use trained model for prediction with confidence
    role, confidence_score = predict_role_with_confidence(skills)
    resume_id = str(uuid.uuid4())

    # Convert numpy float to Python float for database storage
    match_score = float(confidence_score)

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO resumes (id, user_email, raw_text, extracted_skills, predicted_role, match_score, created_at)
                VALUES (:id, :email, :raw, :skills, :role, :match_score, :created_at)
            """), {
                "id": resume_id,
                "email": payload.user_email,
                "raw": payload.resume_text,
                "skills": skills,
                "role": role,
                "match_score": match_score,
                "created_at": datetime.utcnow()
            })
    except OperationalError as e:
        raise HTTPException(status_code=500, detail="Database insert failed")

    return {
        "id": resume_id,
        "skills": skills,
        "predicted_role": role,
        "match_score": match_score
    }

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/retrain")
def retrain():
    try:
        retrain_model()
        # Reload the model after retraining
        from model_utils import reload_model
        if reload_model():
            return {"status": "success", "message": "Model retrained and reloaded successfully"}
        else:
            return {"status": "warning", "message": "Model retrained but failed to reload"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
    
@app.post("/predict")
def predict_skills(payload: PredictRequest):
    try:
        # Use the same prediction function as /analyze endpoint
        role, confidence_score = predict_role_with_confidence(payload.skills)
        
        # Convert numpy float to Python float
        match_score = float(confidence_score)
        
        return {
            "predicted_role": role,
            "match_score": match_score
        }

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Model not found. Please retrain first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirm-role")
def confirm_role(payload: ConfirmRoleRequest):
    try:
        with engine.begin() as conn:
            # Update the confirmed_role for the given resume_id
            result = conn.execute(text("""
                UPDATE resumes 
                SET confirmed_role = :confirmed_role 
                WHERE id = :resume_id
                RETURNING id, predicted_role, confirmed_role
            """), {
                "resume_id": payload.resume_id,
                "confirmed_role": payload.confirmed_role
            })
            
            updated_record = result.fetchone()
            
            if not updated_record:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            return {
                "id": updated_record[0],
                "predicted_role": updated_record[1],
                "confirmed_role": updated_record[2],
                "message": "Role confirmed successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm role: {str(e)}")

@app.get("/resumes")
def get_resumes():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, user_email, predicted_role, confirmed_role, match_score, created_at 
                FROM resumes 
                ORDER BY created_at DESC 
                LIMIT 100
            """))
            
            resumes = []
            for row in result:
                resumes.append({
                    "id": row[0],
                    "user_email": row[1],
                    "predicted_role": row[2],
                    "confirmed_role": row[3],
                    "match_score": row[4],
                    "created_at": row[5].isoformat() if row[5] else None
                })
            
            return {"resumes": resumes}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch resumes: {str(e)}")

@app.get("/skills")
def get_available_skills():
    """
    Get all available skills organized by category
    """
    try:
        return {
            "skills": skill_extractor.get_skill_categories(),
            "total_skills": len(skill_extractor.all_skills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch skills: {str(e)}")

@app.post("/extract-skills")
def extract_skills_from_text(payload: dict):
    """
    Extract skills from text without saving to database
    """
    try:
        text = payload.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        skills = skill_extractor.extract_skills(text)
        return {
            "extracted_skills": skills,
            "skill_count": len(skills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract skills: {str(e)}")