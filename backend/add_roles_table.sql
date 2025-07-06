-- Add roles table to existing database
-- Run this script if you have an existing database without the roles table

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Insert default roles
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

-- Verify the table was created
SELECT COUNT(*) as total_roles FROM roles; 