create extension if not exists "pgcrypto";

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

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

-- Seed roles data
INSERT INTO roles (name, description) VALUES 
('Full Stack Developer', 'Develops both frontend and backend applications'),
('Frontend Developer', 'Specializes in user interface and client-side development'),
('Backend Developer', 'Focuses on server-side logic and database management'),
('Data Scientist', 'Analyzes complex data sets and builds predictive models'),
('Data Analyst', 'Interprets data and provides insights for business decisions'),
('DevOps Engineer', 'Manages infrastructure and deployment pipelines'),
('Mobile Developer', 'Develops applications for mobile devices'),
('UI/UX Designer', 'Designs user interfaces and user experiences'),
('Product Manager', 'Manages product development and strategy'),
('QA Engineer', 'Ensures software quality through testing'),
('Machine Learning Engineer', 'Builds and deploys machine learning models'),
('Cloud Engineer', 'Manages cloud infrastructure and services'),
('Security Engineer', 'Ensures application and infrastructure security'),
('Database Administrator', 'Manages and optimizes database systems'),
('Network Engineer', 'Designs and maintains network infrastructure'),
('System Administrator', 'Manages server systems and IT infrastructure'),
('Software Architect', 'Designs software system architecture'),
('Technical Lead', 'Leads technical teams and makes architectural decisions'),
('Scrum Master', 'Facilitates agile development processes'),
('Business Analyst', 'Analyzes business requirements and processes')
ON CONFLICT (name) DO NOTHING;

-- Seed data
INSERT INTO resumes (user_email, raw_text, extracted_skills, predicted_role, confirmed_role)
VALUES 
('user1@example.com', 'Experienced in Python and React development...', ARRAY['Python', 'React'], 'Full Stack Developer', 'Full Stack Developer'),
('user2@example.com', 'Worked on data cleaning and visualization using pandas and matplotlib', ARRAY['pandas', 'matplotlib'], 'Data Analyst', 'Data Analyst'),
('user3@example.com', 'Built APIs using Node.js and Express with MongoDB', ARRAY['Node.js', 'Express', 'MongoDB'], 'Backend Developer', 'Backend Developer');


-- postgresql://postgres:password@db.abvewuoaeolzsmkiajqe.supabase.co:5432/postgres