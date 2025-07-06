# model_utils.py
import os
import joblib

# Load model and label binarizer
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

try:
    model, mlb = joblib.load(MODEL_PATH)
    print("✅ Loaded model successfully.")
except Exception as e:
    print("❌ Failed to load model:", e)
    model, mlb = None, None

def predict_role_from_skills(skills: list[str]) -> str:
    if not model or not mlb:
        return "Unknown (Model not loaded)"
    
    # Join list into space-separated string
    skill_vector = mlb.transform([" ".join(skills)])
    prediction = model.predict(skill_vector)
    return prediction[0]

def predict_role_with_confidence(skills: list[str]) -> tuple[str, float]:
    """
    Predict role and return confidence score (probability)
    Returns: (predicted_role, confidence_score)
    """
    if not model or not mlb:
        return "Unknown (Model not loaded)", 0.0
    
    # Join list into space-separated string
    skill_vector = mlb.transform([" ".join(skills)])
    
    # Get prediction
    prediction = model.predict(skill_vector)
    predicted_role = prediction[0]
    
    # Get probability for the predicted class
    probabilities = model.predict_proba(skill_vector)
    predicted_class_index = list(model.classes_).index(predicted_role)
    confidence_score = probabilities[0][predicted_class_index]
    
    return predicted_role, confidence_score

