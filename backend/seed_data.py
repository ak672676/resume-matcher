#!/usr/bin/env python3
"""
Seed Data Generator for Resume Matcher
Generates 500+ realistic resume records with diverse roles and skills
"""

import os
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Define comprehensive skill sets for different roles
SKILL_SETS = {
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Node.js", "Express", 
        "Python", "Django", "Flask", "PostgreSQL", "MongoDB", "Redis", "Docker", "AWS", 
        "Git", "REST API", "GraphQL", "HTML", "CSS", "Sass", "Webpack", "Jest", "Cypress"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "HTML", "CSS", "Sass", 
        "Less", "Bootstrap", "Tailwind CSS", "Webpack", "Vite", "Jest", "Cypress", 
        "Redux", "Vuex", "NgRx", "Axios", "Fetch API", "Responsive Design", "PWA"
    ],
    "Backend Developer": [
        "Python", "Java", "C#", "Node.js", "Go", "Rust", "PostgreSQL", "MySQL", "MongoDB", 
        "Redis", "Elasticsearch", "Docker", "Kubernetes", "AWS", "Azure", "GCP", 
        "REST API", "GraphQL", "gRPC", "Microservices", "Spring Boot", "Django", "Flask", 
        "Express", "FastAPI", "JUnit", "PyTest", "Postman"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", 
        "Matplotlib", "Seaborn", "Plotly", "Jupyter", "Apache Spark", "Hadoop", 
        "Tableau", "Power BI", "Statistics", "Machine Learning", "Deep Learning", 
        "Natural Language Processing", "Computer Vision", "A/B Testing"
    ],
    "Data Analyst": [
        "SQL", "Python", "R", "Excel", "Tableau", "Power BI", "Google Analytics", 
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Jupyter", "Statistics", 
        "Data Visualization", "ETL", "Data Cleaning", "Business Intelligence", "A/B Testing"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "AWS", "Azure", 
        "GCP", "Terraform", "Ansible", "Chef", "Puppet", "Linux", "Bash", "Python", 
        "Go", "Prometheus", "Grafana", "ELK Stack", "Nginx", "Apache", "Vagrant"
    ],
    "Mobile Developer": [
        "Swift", "Objective-C", "Kotlin", "Java", "React Native", "Flutter", "Xamarin", 
        "iOS", "Android", "Xcode", "Android Studio", "Firebase", "REST API", "JSON", 
        "Git", "CocoaPods", "Gradle", "App Store", "Google Play", "Push Notifications"
    ],
    "UI/UX Designer": [
        "Figma", "Sketch", "Adobe XD", "InVision", "Adobe Photoshop", "Adobe Illustrator", 
        "HTML", "CSS", "JavaScript", "Prototyping", "User Research", "Wireframing", 
        "Design Systems", "Accessibility", "Responsive Design", "User Testing", "A/B Testing"
    ],
    "Product Manager": [
        "Product Strategy", "Market Research", "User Stories", "Agile", "Scrum", "Kanban", 
        "Jira", "Confluence", "A/B Testing", "Analytics", "SQL", "Excel", "PowerPoint", 
        "Customer Development", "Roadmapping", "Competitive Analysis", "Stakeholder Management"
    ],
    "QA Engineer": [
        "Selenium", "Cypress", "Jest", "PyTest", "JUnit", "TestNG", "Postman", "REST API", 
        "SQL", "Git", "Jenkins", "Jira", "TestRail", "Manual Testing", "Automated Testing", 
        "Performance Testing", "Load Testing", "Security Testing", "Mobile Testing"
    ],
    "Machine Learning Engineer": [
        "Python", "TensorFlow", "PyTorch", "Scikit-learn", "NumPy", "Pandas", "SQL", 
        "Docker", "Kubernetes", "AWS SageMaker", "MLflow", "Kubeflow", "Apache Spark", 
        "Hadoop", "Jupyter", "Git", "REST API", "Microservices", "Model Deployment", 
        "Feature Engineering", "MLOps"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", 
        "GitLab CI", "Python", "Bash", "Linux", "Networking", "Security", "Monitoring", 
        "Logging", "Serverless", "Lambda", "ECS", "EKS", "CloudFormation"
    ],
    "Security Engineer": [
        "Penetration Testing", "Vulnerability Assessment", "SIEM", "IDS/IPS", "Firewall", 
        "VPN", "Encryption", "PKI", "OAuth", "OIDC", "SAML", "Python", "Bash", "Linux", 
        "Wireshark", "Metasploit", "Burp Suite", "Nmap", "Security Auditing", "Compliance"
    ],
    "Database Administrator": [
        "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MongoDB", "Redis", "Elasticsearch", 
        "SQL", "Database Design", "Performance Tuning", "Backup & Recovery", "Replication", 
        "Sharding", "Monitoring", "Linux", "Shell Scripting", "Python", "Automation"
    ],
    "Network Engineer": [
        "Cisco", "Juniper", "Routing", "Switching", "BGP", "OSPF", "EIGRP", "VLAN", 
        "VPN", "Firewall", "Load Balancing", "SDN", "Network Security", "Wireshark", 
        "Python", "Ansible", "Linux", "Monitoring", "Troubleshooting", "Network Design"
    ]
}

# Sample resume text templates
RESUME_TEMPLATES = [
    "Experienced {role} with {years} years of expertise in {skills}. Proven track record of delivering high-quality solutions and collaborating with cross-functional teams.",
    "Passionate {role} skilled in {skills}. Strong problem-solving abilities and experience in agile development methodologies.",
    "Results-driven {role} with deep knowledge of {skills}. Committed to writing clean, maintainable code and staying current with industry best practices.",
    "Innovative {role} with expertise in {skills}. Experience leading technical projects and mentoring junior developers.",
    "Detail-oriented {role} proficient in {skills}. Strong analytical skills and experience in optimizing performance and scalability.",
    "Creative {role} with solid foundation in {skills}. Experience in full software development lifecycle and continuous integration/deployment.",
    "Strategic {role} with hands-on experience in {skills}. Proven ability to translate business requirements into technical solutions.",
    "Collaborative {role} with strong background in {skills}. Experience working in fast-paced environments and delivering projects on time.",
    "Technical {role} with comprehensive knowledge of {skills}. Passionate about learning new technologies and solving complex problems.",
    "Dedicated {role} with expertise in {skills}. Strong communication skills and experience working with stakeholders at all levels."
]

# Sample email domains
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com", 
    "techcorp.com", "startup.io", "enterprise.com", "consulting.com"
]

def generate_random_skills(role: str, min_skills: int = 3, max_skills: int = 8) -> List[str]:
    """Generate random skills for a given role"""
    available_skills = SKILL_SETS.get(role, ["Python", "JavaScript", "SQL", "Git"])
    num_skills = random.randint(min_skills, max_skills)
    return random.sample(available_skills, min(num_skills, len(available_skills)))

def generate_resume_text(role: str, skills: List[str]) -> str:
    """Generate realistic resume text"""
    years = random.randint(1, 8)
    skill_text = ", ".join(random.sample(skills, min(3, len(skills))))
    template = random.choice(RESUME_TEMPLATES)
    return template.format(role=role, years=years, skills=skill_text)

def generate_email() -> str:
    """Generate random email address"""
    first_names = ["john", "jane", "mike", "sarah", "david", "emma", "alex", "lisa", "chris", "anna"]
    last_names = ["smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    domain = random.choice(EMAIL_DOMAINS)
    
    return f"{first}.{last}@{domain}"

def generate_match_score() -> float:
    """Generate realistic match score"""
    return round(random.uniform(0.6, 0.95), 2)

def create_engine_and_connect():
    """Create database engine and test connection"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully")
        return engine
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

def seed_database(num_records: int = 500):
    """Seed the database with sample resume data"""
    engine = create_engine_and_connect()
    
    roles = list(SKILL_SETS.keys())
    
    print(f"🚀 Starting to seed {num_records} records...")
    
    with engine.begin() as conn:
        for i in range(num_records):
            # Generate random data
            role = random.choice(roles)
            skills = generate_random_skills(role)
            resume_text = generate_resume_text(role, skills)
            email = generate_email()
            match_score = generate_match_score()
            
            # Randomly decide if role is confirmed (70% chance)
            confirmed_role = role if random.random() < 0.7 else None
            
            # Generate random creation date within last 2 years
            days_ago = random.randint(0, 730)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            try:
                conn.execute(text("""
                    INSERT INTO resumes (id, user_email, raw_text, extracted_skills, 
                                       predicted_role, confirmed_role, match_score, created_at)
                    VALUES (:id, :email, :raw_text, :skills, :predicted_role, 
                           :confirmed_role, :match_score, :created_at)
                """), {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "raw_text": resume_text,
                    "skills": skills,
                    "predicted_role": role,
                    "confirmed_role": confirmed_role,
                    "match_score": match_score,
                    "created_at": created_at
                })
                
                if (i + 1) % 50 == 0:
                    print(f"✅ Inserted {i + 1} records...")
                    
            except Exception as e:
                print(f"❌ Error inserting record {i + 1}: {e}")
                continue
    
    print(f"🎉 Successfully seeded {num_records} records!")
    
    # Print summary statistics
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as total FROM resumes"))
        total = result.fetchone()[0]
        
        result = conn.execute(text("SELECT predicted_role, COUNT(*) FROM resumes GROUP BY predicted_role ORDER BY COUNT(*) DESC"))
        role_counts = result.fetchall()
        
        result = conn.execute(text("SELECT COUNT(*) FROM resumes WHERE confirmed_role IS NOT NULL"))
        confirmed_count = result.fetchone()[0]
        
        print(f"\n📊 Database Summary:")
        print(f"   Total records: {total}")
        print(f"   Confirmed roles: {confirmed_count}")
        print(f"   Unconfirmed roles: {total - confirmed_count}")
        print(f"\n📈 Records by role:")
        for role, count in role_counts:
            print(f"   {role}: {count}")

if __name__ == "__main__":
    import sys
    
    # Allow custom number of records via command line argument
    num_records = 500
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
        except ValueError:
            print("Invalid number provided. Using default 500 records.")
    
    print(f"🌱 Resume Matcher Seed Data Generator")
    print(f"   Target records: {num_records}")
    print(f"   Available roles: {len(SKILL_SETS)}")
    print(f"   Total skills: {sum(len(skills) for skills in SKILL_SETS.values())}")
    print()
    
    try:
        seed_database(num_records)
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1) 