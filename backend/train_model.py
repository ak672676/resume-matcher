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
    df = pd.read_sql("SELECT extracted_skills, confirmed_role FROM resumes WHERE confirmed_role IS NOT NULL", conn)

    if df.empty:
        print("No training data found.")
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
