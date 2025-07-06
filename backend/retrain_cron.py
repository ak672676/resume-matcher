import os
import joblib
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+psycopg2", "postgresql")

def retrain_model():
    print("🔁 Starting retraining...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql("SELECT extracted_skills, confirmed_role FROM resumes WHERE confirmed_role IS NOT NULL", conn)

        if df.empty:
            print("⚠️ No confirmed resume records to retrain on.")
            return

        print(f"📊 Found {len(df)} confirmed resumes for training")
        
        # Debug: Check the data format
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
            print("⚠️ No records with valid skills found.")
            return

        # Show distribution of confirmed roles
        role_counts = df["confirmed_role"].value_counts()
        print("📈 Role distribution:")
        for role, count in role_counts.items():
            print(f"   {role}: {count}")

        # Use the same preprocessing as train_model.py
        mlb = MultiLabelBinarizer()
        X = mlb.fit_transform(df["extracted_skills"])
        y = df["confirmed_role"]

        # Check if we have enough data for each role (at least 2 samples per role)
        min_samples_per_role = 2
        role_counts = df["confirmed_role"].value_counts()
        insufficient_roles = role_counts[role_counts < min_samples_per_role]
        
        if not insufficient_roles.empty:
            print(f"⚠️ Warning: Some roles have fewer than {min_samples_per_role} samples:")
            for role, count in insufficient_roles.items():
                print(f"   {role}: {count} samples")
            print("   Consider confirming more roles for better model performance.")

        # Use LogisticRegression for consistent probability estimates
        clf = LogisticRegression(random_state=42, max_iter=1000)
        clf.fit(X, y)

        # Save model + binarizer (same format as train_model.py)
        joblib.dump((clf, mlb), "model.pkl")

        print(f"✅ Retrained on {len(df)} samples with {len(clf.classes_)} classes")
        print(f"📈 Classes: {list(clf.classes_)}")

        conn.close()
        
    except Exception as e:
        print(f"❌ Retraining failed: {str(e)}")
        raise

if __name__ == "__main__":
    retrain_model()
