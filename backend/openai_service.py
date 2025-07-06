import os
import openai
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_skills_ai(self, resume_text: str) -> List[str]:
        """Extract skills using OpenAI GPT-3.5-turbo"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a technical recruiter. Extract technical skills, tools, and technologies from the resume text. 
                        Return only a JSON array of skill names, no explanations. Focus on programming languages, frameworks, databases, cloud platforms, and tools."""
                    },
                    {
                        "role": "user", 
                        "content": f"Extract technical skills from this resume: {resume_text[:2000]}"
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            skills_text = response.choices[0].message.content.strip()
            import json
            try:
                skills = json.loads(skills_text)
                return skills if isinstance(skills, list) else []
            except:
                return [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "429" in error_msg:
                print("OpenAI quota exceeded - falling back to traditional methods")
            else:
                print(f"OpenAI API error: {e}")
            return []
    
    def suggest_role_ai(self, skills: List[str], resume_text: str) -> Dict[str, float]:
        """Suggest roles with confidence scores using AI"""
        try:
            skills_text = ", ".join(skills[:10])  # Limit to top 10 skills
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a technical recruiter. Based on the skills and resume context, suggest the most likely job roles. 
                        Return a JSON object with role names as keys and confidence scores (0-1) as values."""
                    },
                    {
                        "role": "user",
                        "content": f"Skills: {skills_text}\nResume context: {resume_text[:500]}\nSuggest roles with confidence scores."
                    }
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content.strip()
            import json
            try:
                return json.loads(result_text)
            except:
                return {"Unknown": 0.5}
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {"Unknown": 0.5}
    
    def generate_resume_feedback(self, resume_text: str, predicted_role: str) -> str:
        """Generate AI-powered resume feedback"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume reviewer. Provide constructive feedback to improve the resume for the target role."
                    },
                    {
                        "role": "user",
                        "content": f"Review this resume for a {predicted_role} position and provide 2-3 specific improvement suggestions: {resume_text[:1500]}"
                    }
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Unable to generate feedback at this time."
    
    def enhance_skill_extraction(self, resume_text: str, existing_skills: List[str]) -> List[str]:
        """Enhance skill extraction with AI insights"""
        try:
            existing_skills_text = ", ".join(existing_skills)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical recruiter. Review the resume and suggest additional technical skills that might be missing from the existing list."
                    },
                    {
                        "role": "user",
                        "content": f"Resume: {resume_text[:1500]}\nExisting skills: {existing_skills_text}\nSuggest additional technical skills (return as JSON array)."
                    }
                ],
                max_tokens=200,
                temperature=0.2
            )
            result_text = response.choices[0].message.content.strip()
            import json
            try:
                additional_skills = json.loads(result_text)
                return additional_skills if isinstance(additional_skills, list) else []
            except:
                return []
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "429" in error_msg:
                print("OpenAI quota exceeded - falling back to traditional methods")
            else:
                print(f"OpenAI API error: {e}")
            return []

# Global instance
openai_service = OpenAIService() 