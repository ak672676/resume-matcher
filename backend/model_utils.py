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
    
    skill_vector = mlb.transform([skills])
    prediction = model.predict(skill_vector)
    return prediction[0]
