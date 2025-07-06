#!/usr/bin/env python3
"""
Debug script to test model predictions
"""

import pickle
import os

def debug_model():
    print("🔍 Debugging Model Issues\n")
    print("=" * 50)
    
    # Test 1: Check if model file exists
    if not os.path.exists("model.pkl"):
        print("❌ Model file not found!")
        return
    
    print(f"✅ Model file exists: {os.path.getsize('model.pkl')} bytes")
    
    # Test 2: Try to load model
    try:
        with open("model.pkl", "rb") as f:
            model_data = pickle.load(f)
        
        print("✅ Model loaded successfully")
        
        if isinstance(model_data, tuple) and len(model_data) == 2:
            model, mlb = model_data
            print(f"📊 Model type: {type(model)}")
            print(f"📈 MLB type: {type(mlb)}")
            
            # Check model classes
            if hasattr(model, 'classes_'):
                classes = list(model.classes_)
                print(f"📊 Model classes ({len(classes)}): {classes}")
                
                # Check for UI/UX Designer
                if "UI/UX Designer" in classes:
                    print("⚠️  UI/UX Designer found in model classes")
                else:
                    print("✅ UI/UX Designer NOT in model classes")
            else:
                print("❌ Model doesn't have classes_ attribute")
                
            # Test 3: Test prediction with sample data
            print(f"\n🧪 Testing predictions:")
            
            test_cases = [
                ["python", "pandas", "numpy", "scikit-learn"],
                ["javascript", "react", "node.js", "express"],
                ["docker", "kubernetes", "aws", "terraform"],
                ["sql", "postgresql", "mysql", "redis"]
            ]
            
            for i, skills in enumerate(test_cases, 1):
                try:
                    # Test with MultiLabelBinarizer
                    skill_vector = mlb.transform([skills])
                    prediction = model.predict(skill_vector)
                    predicted_role = prediction[0]
                    
                    print(f"   Test {i} ({skills}): {predicted_role}")
                    
                    if predicted_role == "UI/UX Designer":
                        print(f"      🚨 PROBLEM: Predicting UI/UX Designer!")
                    elif predicted_role in classes:
                        print(f"      ✅ Valid prediction")
                    else:
                        print(f"      ⚠️  Unknown prediction: {predicted_role}")
                        
                except Exception as e:
                    print(f"   Test {i} failed: {e}")
                    
        else:
            print(f"❌ Unexpected model format: {type(model_data)}")
            
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    debug_model() 