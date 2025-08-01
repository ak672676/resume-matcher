import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_skills_ai(self, resume_text: str) -> List[str]:
        """Extract skills using Google Gemini"""
        try:
            prompt = f"""You are a technical recruiter. Extract technical skills, tools, and technologies from this resume text.
            Return ONLY a JSON array of skill names, no explanations. Focus on programming languages, frameworks, databases, cloud platforms, and tools.
            
            Resume text: {resume_text[:2000]}
            
            Return format: ["skill1", "skill2", "skill3"]"""
            
            response = self.model.generate_content(prompt)
            skills_text = response.text.strip()
            
            # Clean up the response - remove markdown code blocks if present
            if "```json" in skills_text:
                skills_text = skills_text.split("```json")[1].split("```")[0].strip()
            elif "```" in skills_text:
                skills_text = skills_text.split("```")[1].strip()
            
            try:
                skills = json.loads(skills_text)
                return skills if isinstance(skills, list) else []
            except json.JSONDecodeError:
                # Fallback: try to extract array from the text
                import re
                array_match = re.search(r'\[(.*?)\]', skills_text)
                if array_match:
                    array_content = array_match.group(1)
                    # Split by comma and clean up quotes
                    skills = [skill.strip().strip('"\'') for skill in array_content.split(',')]
                    return [skill for skill in skills if skill]
                else:
                    # Final fallback: split by comma
                    return [skill.strip().strip('"\'') for skill in skills_text.split(',') if skill.strip()]
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("Google Gemini quota exceeded - falling back to traditional methods")
                raise Exception("Google Gemini quota exceeded")  # Re-raise to trigger fallback
            else:
                print(f"Google Gemini API error: {e}")
                raise  # Re-raise other errors
    
    def suggest_role_ai(self, skills: List[str], resume_text: str) -> Dict[str, float]:
        """Suggest roles with confidence scores using AI"""
        try:
            skills_text = ", ".join(skills[:10])  # Limit to top 10 skills
            
            prompt = f"""You are a technical recruiter. Based on the skills and resume context, suggest the most likely job roles.
            Return a JSON object with role names as keys and confidence scores (0-1) as values.
            
            Skills: {skills_text}
            Resume context: {resume_text[:500]}
            
            Return format: {{"role1": 0.8, "role2": 0.6}}"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up the response - remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return {"Unknown": 0.5}
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("Google Gemini quota exceeded - falling back to traditional methods")
                raise Exception("Google Gemini quota exceeded")  # Re-raise to trigger fallback
            else:
                print(f"Google Gemini API error: {e}")
                raise  # Re-raise other errors
    
    def generate_resume_feedback(self, resume_text: str, predicted_role: str) -> str:
        """Generate AI-powered resume feedback"""
        try:
            prompt = f"""You are a professional resume reviewer. Provide constructive feedback to improve this resume for a {predicted_role} position.
            Give 2-3 specific improvement suggestions.
            
            Resume: {resume_text[:1500]}
            
            Provide clear, actionable feedback."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("Google Gemini quota exceeded - falling back to traditional methods")
                raise Exception("Google Gemini quota exceeded")  # Re-raise to trigger fallback
            else:
                print(f"Google Gemini API error: {e}")
                raise  # Re-raise other errors
    
    def enhance_skill_extraction(self, resume_text: str, existing_skills: List[str]) -> List[str]:
        """Enhance skill extraction with AI insights"""
        try:
            existing_skills_text = ", ".join(existing_skills)
            
            prompt = f"""You are a technical recruiter. Review this resume and suggest additional technical skills that might be missing from the existing list.
            Return ONLY a JSON array of additional skills.
            
            Resume: {resume_text[:1500]}
            Existing skills: {existing_skills_text}
            
            Return format: ["additional_skill1", "additional_skill2"]"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up the response - remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            try:
                additional_skills = json.loads(result_text)
                return additional_skills if isinstance(additional_skills, list) else []
            except json.JSONDecodeError:
                # Fallback: try to extract array from the text
                import re
                array_match = re.search(r'\[(.*?)\]', result_text)
                if array_match:
                    array_content = array_match.group(1)
                    # Split by comma and clean up quotes
                    skills = [skill.strip().strip('"\'') for skill in array_content.split(',')]
                    return [skill for skill in skills if skill]
                else:
                    return []
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("Google Gemini quota exceeded - falling back to traditional methods")
                raise Exception("Google Gemini quota exceeded")  # Re-raise to trigger fallback
            else:
                print(f"Google Gemini API error: {e}")
                raise  # Re-raise other errors

# Global instance
gemini_service = GeminiService() 