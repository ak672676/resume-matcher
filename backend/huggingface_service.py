import os
import requests
import json
from typing import List, Dict, Optional
import time

class HuggingFaceService:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Model endpoints for different tasks
        self.models = {
            "text_generation": "gpt2",  # More reliable text generation model
            "text_classification": "facebook/bart-large-mnli",  # For skill classification
            "summarization": "facebook/bart-large-cnn",  # For resume feedback
        }
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else None,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, model_name: str, payload: dict, max_retries: int = 3) -> Optional[dict]:
        """Make a request to Hugging Face API with retry logic"""
        url = f"{self.base_url}/{model_name}"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"Model {model_name} is loading, attempt {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"API request failed: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
        
        return None
    
    def suggest_role_ai(self, skills: List[str], resume_text: str) -> Dict[str, float]:
        """Suggest alternative roles based on skills and resume content"""
        try:
            if not self.api_token:
                return {}
            
            # Create a prompt for role suggestion
            skills_text = ", ".join(skills[:10])  # Limit to first 10 skills
            prompt = f"""
            Based on these skills: {skills_text}
            And this resume summary: {resume_text[:500]}...
            
            Suggest 3 alternative job roles that would be a good fit. 
            Return only the role names separated by commas, no explanations.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True,
                    "num_return_sequences": 1
                }
            }
            
            result = self._make_request(self.models["text_generation"], payload)
            
            if result and isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                
                # Extract role suggestions from generated text
                roles = []
                lines = generated_text.split('\n')
                for line in lines:
                    if ',' in line and any(role_word in line.lower() for role_word in ['developer', 'engineer', 'analyst', 'manager', 'specialist', 'designer']):
                        # Extract roles from this line
                        potential_roles = [role.strip() for role in line.split(',')]
                        roles.extend([role for role in potential_roles if len(role) > 3])
                
                # Create confidence scores (decreasing)
                suggestions = {}
                for i, role in enumerate(roles[:3]):
                    confidence = max(0.3, 0.9 - (i * 0.2))  # 90%, 70%, 50%
                    suggestions[role] = confidence
                
                return suggestions
            
            return {}
            
        except Exception as e:
            print(f"Hugging Face role suggestion failed: {e}")
            return {}
    
    def generate_resume_feedback(self, resume_text: str, target_role: str) -> str:
        """Generate AI-powered resume feedback"""
        try:
            if not self.api_token:
                return ""
            
            # Create a prompt for resume feedback
            prompt = f"""
            Analyze this resume for a {target_role} position and provide constructive feedback.
            
            Resume: {resume_text[:1000]}...
            
            Provide feedback in this format:
            1. Overall assessment (2-3 sentences)
            2. Three specific improvement suggestions with actionable steps
            3. One concrete example of how to improve
            
            Keep the feedback constructive and actionable.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.6,
                    "do_sample": True,
                    "num_return_sequences": 1
                }
            }
            
            result = self._make_request(self.models["text_generation"], payload)
            
            if result and isinstance(result, list) and len(result) > 0:
                feedback = result[0].get("generated_text", "")
                
                # Clean up the feedback
                feedback = feedback.replace(prompt, "").strip()
                if feedback.startswith("Based on"):
                    feedback = feedback.split("\n", 1)[1] if "\n" in feedback else feedback
                
                return feedback if len(feedback) > 50 else ""
            
            return ""
            
        except Exception as e:
            print(f"Hugging Face feedback generation failed: {e}")
            return ""
    
    def enhance_skill_extraction(self, text: str, existing_skills: List[str]) -> List[str]:
        """Enhance skill extraction using AI"""
        try:
            if not self.api_token:
                return []
            
            # Create a prompt for skill enhancement
            existing_skills_text = ", ".join(existing_skills)
            prompt = f"""
            Given these existing skills: {existing_skills_text}
            And this resume text: {text[:800]}...
            
            Suggest 5 additional relevant technical skills that might be missing.
            Return only skill names separated by commas, no explanations.
            """
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.5,
                    "do_sample": True,
                    "num_return_sequences": 1
                }
            }
            
            result = self._make_request(self.models["text_generation"], payload)
            
            if result and isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                
                # Extract skills from generated text
                skills = []
                lines = generated_text.split('\n')
                for line in lines:
                    if ',' in line:
                        potential_skills = [skill.strip() for skill in line.split(',')]
                        skills.extend([skill for skill in potential_skills if len(skill) > 2 and skill not in existing_skills])
                
                return skills[:5]  # Return max 5 additional skills
            
            return []
            
        except Exception as e:
            print(f"Hugging Face skill enhancement failed: {e}")
            return []
    
    def classify_skills(self, skills: List[str], categories: List[str]) -> Dict[str, List[str]]:
        """Classify skills into categories using zero-shot classification"""
        try:
            if not self.api_token or not skills:
                return {}
            
            # Use BART for zero-shot classification
            payload = {
                "inputs": skills,
                "parameters": {
                    "candidate_labels": categories,
                    "multi_label": True
                }
            }
            
            result = self._make_request(self.models["text_classification"], payload)
            
            if result and isinstance(result, list):
                classifications = {}
                for i, skill in enumerate(skills):
                    if i < len(result):
                        labels = result[i].get("labels", [])
                        scores = result[i].get("scores", [])
                        
                        # Get the best category for this skill
                        if labels and scores:
                            best_label = labels[0]
                            if best_label not in classifications:
                                classifications[best_label] = []
                            classifications[best_label].append(skill)
                
                return classifications
            
            return {}
            
        except Exception as e:
            print(f"Hugging Face skill classification failed: {e}")
            return {}

# Global instance
huggingface_service = HuggingFaceService() 