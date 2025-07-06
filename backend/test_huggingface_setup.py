#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration
"""

import os
from dotenv import load_dotenv
from huggingface_service import huggingface_service

# Load environment variables
load_dotenv()

def test_huggingface_setup():
    """Test Hugging Face token and basic functionality"""
    
    print("🤗 Testing Hugging Face Integration")
    print("=" * 50)
    
    # Check if token is configured
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_API_TOKEN not found in environment")
        print("💡 Add HUGGINGFACE_API_TOKEN=your_token to your .env file")
        return False
    
    print(f"✅ Hugging Face token found: {token[:10]}...")
    
    # Test basic functionality
    try:
        # Test role suggestions
        print("\n🧪 Testing role suggestions...")
        skills = ["python", "javascript", "react", "node.js"]
        resume_text = "Experienced full stack developer with Python and JavaScript skills."
        
        suggestions = huggingface_service.suggest_role_ai(skills, resume_text)
        if suggestions:
            print(f"✅ Role suggestions successful: {list(suggestions.keys())}")
        else:
            print("⚠️ No role suggestions returned")
        
        # Test feedback generation
        print("\n🧪 Testing feedback generation...")
        feedback = huggingface_service.generate_resume_feedback(resume_text, "Software Developer")
        if feedback:
            print(f"✅ Feedback generation successful: {len(feedback)} characters")
            print(f"📝 Preview: {feedback[:100]}...")
        else:
            print("⚠️ No feedback returned")
        
        # Test skill enhancement
        print("\n🧪 Testing skill enhancement...")
        enhanced_skills = huggingface_service.enhance_skill_extraction(resume_text, skills)
        if enhanced_skills:
            print(f"✅ Skill enhancement successful: {enhanced_skills}")
        else:
            print("⚠️ No enhanced skills returned")
        
        print("\n🎉 Hugging Face integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_huggingface_setup() 