# model_utils.py
import os
import joblib

# Model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

def load_model():
    """Load model and label binarizer"""
    try:
        model, mlb = joblib.load(MODEL_PATH)
        return model, mlb
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None, None

# Load model at startup
model, mlb = load_model()
if model is not None:
    print("✅ Loaded model successfully.")
    print(f"📊 Model classes: {list(model.classes_)}")
else:
    print("❌ Model not loaded.")

def predict_role_from_skills(skills: list[str]) -> str:
    if not model or not mlb:
        return "Unknown (Model not loaded)"
    
    # Join list into space-separated string
    skill_vector = mlb.transform([" ".join(skills)])
    prediction = model.predict(skill_vector)
    return prediction[0]

def reload_model():
    """Reload the model from disk"""
    global model, mlb
    model, mlb = load_model()
    if model is not None:
        print("✅ Model reloaded successfully.")
        print(f"📊 Model classes: {list(model.classes_)}")
    return model is not None

def predict_role_with_confidence(skills: list[str]) -> tuple[str, float]:
    """
    Predict role and return confidence score (probability)
    Returns: (predicted_role, confidence_score)
    """
    global model, mlb
    
    # Try to reload model if not loaded
    if not model or not mlb:
        if not reload_model():
            return "Unknown (Model not loaded)", 0.0
    
    try:
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
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return "Unknown (Prediction error)", 0.0

