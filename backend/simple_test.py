#!/usr/bin/env python3
"""
Simple test script to debug model prediction issues
"""

import pickle
import os

def test_model():
    print("🔍 Testing Model Predictions\n")
    print("=" * 50)
    
    # Test 1: Check if model loads
    try:
        with open("model.pkl", "rb") as f:
            model_data = pickle.load(f)
        
        print("✅ Model loaded successfully")
        
        # Check what we loaded
        if isinstance(model_data, tuple) and len(model_data) == 2:
            model, mlb = model_data
            print(f"📊 Model type: {type(model)}")
            print(f"📈 MLB type: {type(mlb)}")
            
            # Try to get classes
            if hasattr(model, 'classes_'):
                print(f"📊 Model classes: {list(model.classes_)}")
                print(f"📈 Number of classes: {len(model.classes_)}")
                
                # Check if UI/UX Designer is in the model classes
                if "UI/UX Designer" in model.classes_:
                    print("⚠️  UI/UX Designer is in model classes (this shouldn't be there)")
                else:
                    print("✅ UI/UX Designer is NOT in model classes (correct)")
            else:
                print("❌ Model doesn't have classes_ attribute")
                
        else:
            print(f"❌ Unexpected model format: {type(model_data)}")
            
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Test 2: Test a simple prediction
    try:
        # Simple test skills
        test_skills = ["python", "javascript", "react", "sql"]
        print(f"\n🧪 Testing with skills: {test_skills}")
        
        # Try to make a prediction
        if hasattr(model, 'predict') and hasattr(mlb, 'transform'):
            # Transform skills
            skill_str = " ".join(test_skills)
            skill_vector = mlb.transform([skill_str])
            
            # Make prediction
            prediction = model.predict(skill_vector)
            predicted_role = prediction[0]
            
            print(f"   Predicted role: {predicted_role}")
            
            if predicted_role == "UI/UX Designer":
                print("   🚨 PROBLEM: Predicting UI/UX Designer!")
            else:
                print("   ✅ Good prediction!")
                
        else:
            print("   ❌ Model doesn't have required methods")
            
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")

if __name__ == "__main__":
    test_model() 