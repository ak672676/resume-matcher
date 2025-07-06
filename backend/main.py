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
from model_utils import predict_role_from_skills

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

# Dummy skill extraction logic
def extract_skills(text: str) -> List[str]:
    keywords = ["python", "react", "node", "sql", "docker", "aws", "pandas", "matplotlib", "express", "mongodb"]
    return [word for word in keywords if word.lower() in text.lower()]

# Input schema
class ResumeInput(BaseModel):
    user_email: str
    resume_text: str
    
class PredictRequest(BaseModel):
    skills: List[str]


# Main API route
@app.post("/analyze")
def analyze_resume(payload: ResumeInput):
    skills = extract_skills(payload.resume_text)
    
    # ✅ Use trained model for prediction
    role = predict_role_from_skills(skills)
    resume_id = str(uuid.uuid4())

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO resumes (id, user_email, raw_text, extracted_skills, predicted_role, created_at)
                VALUES (:id, :email, :raw, :skills, :role, :created_at)
            """), {
                "id": resume_id,
                "email": payload.user_email,
                "raw": payload.resume_text,
                "skills": skills,
                "role": role,
                "created_at": datetime.utcnow()
            })
    except OperationalError as e:
        raise HTTPException(status_code=500, detail="Database insert failed")

    return {
        "id": resume_id,
        "skills": skills,
        "predicted_role": role
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
        return {"status": "success", "message": "Model retrained successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
    
@app.post("/predict")
def predict_skills(payload: PredictRequest):
    try:
        # Load trained model
        with open("model.pkl", "rb") as f:
            model, vectorizer = pickle.load(f)

        # Convert skills to space-separated string
        skill_str = " ".join(payload.skills)
        X = vectorizer.transform([skill_str])
        predicted_role = model.predict(X)[0]

        return {"predicted_role": predicted_role}

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Model not found. Please retrain first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))