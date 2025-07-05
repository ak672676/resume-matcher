create extension if not exists "pgcrypto";

CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_email TEXT,
  raw_text TEXT NOT NULL,
  extracted_skills TEXT[],
  predicted_role TEXT,
  confirmed_role TEXT,
  match_score FLOAT,
  created_at TIMESTAMP DEFAULT now()
);

-- Seed data
INSERT INTO resumes (user_email, raw_text, extracted_skills, predicted_role, confirmed_role)
VALUES 
('user1@example.com', 'Experienced in Python and React development...', ARRAY['Python', 'React'], 'Full Stack Developer', 'Full Stack Developer'),
('user2@example.com', 'Worked on data cleaning and visualization using pandas and matplotlib', ARRAY['pandas', 'matplotlib'], 'Data Analyst', 'Data Analyst'),
('user3@example.com', 'Built APIs using Node.js and Express with MongoDB', ARRAY['Node.js', 'Express', 'MongoDB'], 'Backend Developer', 'Backend Developer');


-- postgresql://postgres:password@db.abvewuoaeolzsmkiajqe.supabase.co:5432/postgres