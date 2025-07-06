# train_model.py
import os
import joblib
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+psycopg2", "postgresql")

def train():
    conn = psycopg2.connect(DATABASE_URL)
    
    # Get training data from resumes with confirmed roles
    # Also include roles from the roles table as fallback
    df = pd.read_sql("""
        SELECT r.extracted_skills, r.confirmed_role 
        FROM resumes r 
        WHERE r.confirmed_role IS NOT NULL
        UNION ALL
        SELECT ARRAY['Sample Skill'] as extracted_skills, ro.name as confirmed_role
        FROM roles ro
        WHERE ro.is_active = TRUE
        AND ro.name NOT IN (SELECT DISTINCT confirmed_role FROM resumes WHERE confirmed_role IS NOT NULL)
    """, conn)

    if df.empty:
        print("No training data found.")
        return

    # Debug: Check the data format
    print(f"📊 Found {len(df)} records for training")
    print(f"📈 Sample skills format: {df['extracted_skills'].iloc[0]} (type: {type(df['extracted_skills'].iloc[0])})")
    
    # Ensure skills are in the correct format (list of strings)
    # PostgreSQL arrays might be read as strings or other formats
    def normalize_skills(skills):
        if skills is None:
            return []
        if isinstance(skills, str):
            # If it's a string, try to parse it
            import ast
            try:
                return ast.literal_eval(skills)
            except:
                return [skills]
        elif isinstance(skills, list):
            return skills
        else:
            return [str(skills)]
    
    df['extracted_skills'] = df['extracted_skills'].apply(normalize_skills)
    
    # Filter out empty skill lists
    df = df[df['extracted_skills'].apply(len) > 0]
    
    if df.empty:
        print("No records with valid skills found.")
        return

    mlb = MultiLabelBinarizer()
    X = mlb.fit_transform(df["extracted_skills"])
    y = df["confirmed_role"]

    # Use LogisticRegression for better probability estimates
    # RandomForest can also output probabilities but LogisticRegression is more calibrated
    clf = LogisticRegression(random_state=42, max_iter=1000)
    clf.fit(X, y)

    joblib.dump((clf, mlb), "model.pkl")
    print("✅ Model trained and saved as model.pkl")
    print(f"✅ Trained on {len(df)} samples with {len(clf.classes_)} classes")

if __name__ == "__main__":
    train()
