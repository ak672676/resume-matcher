import os
import pickle
import psycopg2
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+psycopg2", "postgresql")

def retrain_model():
    print("🔁 Starting retraining...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Get rows where confirmed_role is available (i.e., labeled)
    cursor.execute("""
        SELECT extracted_skills, confirmed_role
        FROM resumes
        WHERE confirmed_role IS NOT NULL
    """)
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No confirmed resume records to retrain on.")
        return

    # Preprocessing
    skill_texts = [" ".join(skills) for skills, _ in rows]
    roles = [label for _, label in rows]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(skill_texts)
    y = roles

    model = MultinomialNB()
    model.fit(X, y)

    # Save model + vectorizer
    with open("model.pkl", "wb") as f:
        pickle.dump((model, vectorizer), f)

    print(f"✅ Retrained on {len(rows)} samples.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    retrain_model()
