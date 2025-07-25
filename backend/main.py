import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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
from gemini_service import gemini_service
from huggingface_service import huggingface_service
from pdf_processor import pdf_processor

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

def extract_skills(text: str) -> List[str]:
    # Use traditional skill extraction
    traditional_skills = skill_extractor.extract_skills(text)
    
    # Try to enhance with AI - Google first, then Hugging Face
    ai_skills = []
    ai_provider = "none"
    
    # Try Google Gemini first
    if os.getenv("GOOGLE_API_KEY"):
        try:
            ai_skills = gemini_service.extract_skills_ai(text)
            ai_provider = "google"
            print(f"✅ Google Gemini skill extraction successful")
        except Exception as e:
            print(f"❌ Google Gemini skill extraction failed: {e}")
            # Fallback to Hugging Face
            if os.getenv("HUGGINGFACE_API_TOKEN"):
                try:
                    ai_skills = huggingface_service.enhance_skill_extraction(text, traditional_skills)
                    ai_provider = "huggingface"
                    print(f"✅ Hugging Face skill extraction successful")
                except Exception as hf_e:
                    print(f"❌ Hugging Face skill extraction failed: {hf_e}")
            else:
                print(f"⚠️ No Hugging Face token configured for fallback")
    
    # Combine and deduplicate skills
    if ai_skills:
        all_skills = list(set(traditional_skills + ai_skills))
        print(f"🎯 Combined skills from {ai_provider}: {len(all_skills)} total skills")
        return all_skills[:15]  # Return top 15
    
    return traditional_skills

# Input schema
class ResumeInput(BaseModel):
    user_email: str
    resume_text: str
    
class PredictRequest(BaseModel):
    skills: List[str]

class ConfirmRoleRequest(BaseModel):
    resume_id: str
    confirmed_role: str

class AddRoleRequest(BaseModel):
    name: str
    description: str = ""


# Internal function for resume analysis (used by upload endpoints)
def analyze_resume_internal(payload: ResumeInput):
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

@app.get("/roles")
def get_available_roles():
    """Get all available roles from the roles table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name, description, is_active 
                FROM roles 
                WHERE is_active = TRUE 
                ORDER BY name
            """))
            
            roles = []
            for row in result:
                roles.append({
                    "name": row[0],
                    "description": row[1],
                    "is_active": row[2]
                })
            
            return {
                "roles": roles,
                "total_roles": len(roles)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch roles: {str(e)}")

@app.post("/roles")
def add_new_role(payload: AddRoleRequest):
    """Add a new role to the system"""
    try:
        role_name = payload.name.strip()
        if not role_name:
            raise HTTPException(status_code=400, detail="Role name cannot be empty")
        
        with engine.begin() as conn:
            # Check if role already exists
            result = conn.execute(text("""
                SELECT id FROM roles WHERE name = :name
            """), {"name": role_name})
            
            if result.fetchone():
                return {
                    "message": f"Role '{role_name}' already exists",
                    "role_name": role_name,
                    "status": "exists"
                }
            
            # Add new role
            conn.execute(text("""
                INSERT INTO roles (name, description) 
                VALUES (:name, :description)
            """), {
                "name": role_name,
                "description": payload.description
            })
            
            return {
                "message": f"Role '{role_name}' added successfully",
                "role_name": role_name,
                "status": "added"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add role: {str(e)}")

@app.delete("/roles/{role_name}")
def delete_role(role_name: str):
    """Soft delete a role (mark as inactive)"""
    try:
        with engine.begin() as conn:
            # Check if role is being used
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM resumes 
                WHERE confirmed_role = :role_name OR predicted_role = :role_name
            """), {"role_name": role_name})
            
            count = result.fetchone()[0]
            
            if count > 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot delete role '{role_name}' - it's used by {count} resume(s)"
                )
            
            # Soft delete by marking as inactive
            result = conn.execute(text("""
                UPDATE roles 
                SET is_active = FALSE, updated_at = NOW() 
                WHERE name = :role_name
            """), {"role_name": role_name})
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")
            
            return {
                "message": f"Role '{role_name}' deleted successfully",
                "role_name": role_name
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")

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

def analyze_resume_ai_internal(payload: ResumeInput):
    """Enhanced analysis with AI insights (internal function)"""
    try:
        # Extract skills using both traditional and AI methods
        skills = extract_skills(payload.resume_text)
        
        # Get AI role suggestions - try Google first, then Hugging Face
        ai_suggestions = {}
        ai_provider = "none"
        
        if os.getenv("GOOGLE_API_KEY"):
            try:
                ai_suggestions = gemini_service.suggest_role_ai(skills, payload.resume_text)
                ai_provider = "google"
                print(f"✅ Google Gemini role suggestions successful")
            except Exception as e:
                print(f"❌ Google Gemini role suggestions failed: {e}")
                # Fallback to Hugging Face
                if os.getenv("HUGGINGFACE_API_TOKEN"):
                    try:
                        ai_suggestions = huggingface_service.suggest_role_ai(skills, payload.resume_text)
                        ai_provider = "huggingface"
                        print(f"✅ Hugging Face role suggestions successful")
                    except Exception as hf_e:
                        print(f"❌ Hugging Face role suggestions failed: {hf_e}")
                else:
                    print(f"⚠️ No Hugging Face token configured for role suggestions fallback")
        
        # Use ML model for primary prediction
        role, confidence_score = predict_role_with_confidence(skills)
        match_score = float(confidence_score)
        
        # Generate AI feedback - try Google first, then Hugging Face
        ai_feedback = ""
        if os.getenv("GOOGLE_API_KEY"):
            try:
                ai_feedback = gemini_service.generate_resume_feedback(payload.resume_text, role)
                ai_provider = "google"
                print(f"✅ Google Gemini feedback generation successful")
            except Exception as e:
                print(f"❌ Google Gemini feedback generation failed: {e}")
                # Fallback to Hugging Face
                if os.getenv("HUGGINGFACE_API_TOKEN"):
                    try:
                        ai_feedback = huggingface_service.generate_resume_feedback(payload.resume_text, role)
                        ai_provider = "huggingface"
                        print(f"✅ Hugging Face feedback generation successful")
                    except Exception as hf_e:
                        print(f"❌ Hugging Face feedback generation failed: {hf_e}")
                else:
                    print(f"⚠️ No Hugging Face token configured for feedback fallback")
        
        resume_id = str(uuid.uuid4())
        
        # Save to database
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
            "match_score": match_score,
            "ai_suggestions": ai_suggestions,
            "ai_feedback": ai_feedback,
            "ai_enhanced": ai_provider != "none",
            "ai_provider": ai_provider
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.post("/enhance-skills")
def enhance_skills_ai(payload: dict):
    """Enhance existing skills with AI insights"""
    try:
        text = payload.get("text", "")
        existing_skills = payload.get("skills", [])
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        additional_skills = []
        ai_provider = "none"
        
        # Try Google first, then Hugging Face
        if os.getenv("GOOGLE_API_KEY"):
            try:
                additional_skills = gemini_service.enhance_skill_extraction(text, existing_skills)
                ai_provider = "google"
            except Exception as e:
                print(f"Google skill enhancement failed: {e}")
                # Fallback to Hugging Face
                if os.getenv("HUGGINGFACE_API_TOKEN"):
                    try:
                        additional_skills = huggingface_service.enhance_skill_extraction(text, existing_skills)
                        ai_provider = "huggingface"
                    except Exception as hf_e:
                        print(f"Hugging Face skill enhancement failed: {hf_e}")
        
        if ai_provider == "none":
            raise HTTPException(status_code=400, detail="No AI provider configured (Google API or Hugging Face)")
        
        return {
            "original_skills": existing_skills,
            "additional_skills": additional_skills,
            "enhanced_skills": list(set(existing_skills + additional_skills)),
            "ai_provider": ai_provider
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill enhancement failed: {str(e)}")

@app.post("/generate-feedback")
def generate_resume_feedback_ai(payload: dict):
    """Generate AI-powered resume feedback"""
    try:
        text = payload.get("text", "")
        target_role = payload.get("target_role", "Software Developer")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        feedback = ""
        ai_provider = "none"
        
        # Try Google first, then Hugging Face
        if os.getenv("GOOGLE_API_KEY"):
            try:
                feedback = gemini_service.generate_resume_feedback(text, target_role)
                ai_provider = "google"
            except Exception as e:
                print(f"Google feedback generation failed: {e}")
                # Fallback to Hugging Face
                if os.getenv("HUGGINGFACE_API_TOKEN"):
                    try:
                        feedback = huggingface_service.generate_resume_feedback(text, target_role)
                        ai_provider = "huggingface"
                    except Exception as hf_e:
                        print(f"Hugging Face feedback generation failed: {hf_e}")
        
        if ai_provider == "none":
            raise HTTPException(status_code=400, detail="No AI provider configured (Google API or Hugging Face)")
        
        return {
            "feedback": feedback,
            "target_role": target_role,
            "ai_provider": ai_provider
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    use_ai: bool = Form(False)
):
    """Upload and analyze a PDF resume"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        file_content = await file.read()
        
        # Validate PDF
        is_valid, error_message = pdf_processor.validate_pdf(file_content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Extract text from PDF
        resume_text = pdf_processor.extract_text_from_pdf(file_content)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze the resume
        payload = ResumeInput(user_email=user_email, resume_text=resume_text)
        
        if use_ai:
            result = analyze_resume_ai_internal(payload)
        else:
            result = analyze_resume_internal(payload)
        
        return {
            "message": "Resume uploaded and analyzed successfully",
            "filename": file.filename,
            "file_size": len(file_content),
            "extracted_text_length": len(resume_text),
            "analysis_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@app.post("/upload-resume-text")
async def upload_resume_text(
    user_email: str = Form(...),
    resume_text: str = Form(...),
    use_ai: bool = Form(False)
):
    """Upload resume as text and analyze it"""
    try:
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
        
        # Analyze the resume
        payload = ResumeInput(user_email=user_email, resume_text=resume_text)
        
        if use_ai:
            result = analyze_resume_ai_internal(payload)
        else:
            result = analyze_resume_internal(payload)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze resume: {str(e)}")