#!/usr/bin/env python3
"""
Test script to debug model prediction issues
"""

import joblib
import os
from model_utils import predict_role_with_confidence, predict_role_from_skills

def test_model():
    print("🔍 Testing Model Predictions\n")
    print("=" * 50)
    
    # Test 1: Check if model loads
    try:
        model, mlb = joblib.load("model.pkl")
        print("✅ Model loaded successfully")
        print(f"📊 Model classes: {list(model.classes_)}")
        print(f"📈 Number of classes: {len(model.classes_)}")
        
        # Check if UI/UX Designer is in the model classes
        if "UI/UX Designer" in model.classes_:
            print("⚠️  UI/UX Designer is in model classes (this shouldn't be there)")
        else:
            print("✅ UI/UX Designer is NOT in model classes (correct)")
            
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Test 2: Test different skill combinations
    test_cases = [
        {
            "name": "Full Stack Skills",
            "skills": ["javascript", "react", "node.js", "python", "sql", "docker"]
        },
        {
            "name": "Data Science Skills", 
            "skills": ["python", "pandas", "numpy", "scikit-learn", "matplotlib", "jupyter"]
        },
        {
            "name": "DevOps Skills",
            "skills": ["docker", "kubernetes", "aws", "jenkins", "terraform", "linux"]
        },
        {
            "name": "Frontend Skills",
            "skills": ["javascript", "react", "html", "css", "bootstrap", "webpack"]
        },
        {
            "name": "Backend Skills",
            "skills": ["python", "django", "postgresql", "redis", "docker", "aws"]
        }
    ]
    
    print(f"\n🧪 Testing Predictions:")
    print("-" * 50)
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}:")
        print(f"   Skills: {test_case['skills']}")
        
        # Test both prediction functions
        role1 = predict_role_from_skills(test_case['skills'])
        role2, confidence = predict_role_with_confidence(test_case['skills'])
        
        print(f"   predict_role_from_skills: {role1}")
        print(f"   predict_role_with_confidence: {role2} (confidence: {confidence:.3f})")
        
        if role1 != role2:
            print(f"   ⚠️  WARNING: Different predictions!")
        
        if "UI/UX Designer" in [role1, role2]:
            print(f"   🚨 PROBLEM: Predicting UI/UX Designer!")

if __name__ == "__main__":
    test_model() 