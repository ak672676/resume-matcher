#!/usr/bin/env python3
"""
Test script to demonstrate the improved skill extraction
"""

from skill_extractor import skill_extractor

def test_skill_extraction():
    # Test cases with different types of resume text
    test_cases = [
        {
            "name": "Full Stack Developer Resume",
            "text": """
            Experienced Full Stack Developer with 5 years of expertise in JavaScript, React, Node.js, and Python.
            Proficient in building scalable web applications using modern frameworks and technologies.
            Skills: JavaScript, React, Node.js, Express, MongoDB, PostgreSQL, Docker, AWS, Git
            Technologies: HTML, CSS, Bootstrap, Webpack, Jest, Cypress
            """
        },
        {
            "name": "Data Scientist Resume",
            "text": """
            Data Scientist with strong background in machine learning and statistical analysis.
            Experienced with Python, pandas, numpy, scikit-learn, TensorFlow, and PyTorch.
            Worked on data cleaning, feature engineering, and model deployment using MLflow.
            Tools: Jupyter, Matplotlib, Seaborn, Plotly, Apache Spark, Hadoop
            """
        },
        {
            "name": "DevOps Engineer Resume",
            "text": """
            DevOps Engineer with expertise in CI/CD, containerization, and cloud infrastructure.
            Proficient in Docker, Kubernetes, Jenkins, GitLab CI, AWS, and Terraform.
            Experience with monitoring tools like Prometheus, Grafana, and ELK Stack.
            Technologies: Linux, Bash, Python, Ansible, Vault, Consul
            """
        },
        {
            "name": "Mobile Developer Resume",
            "text": """
            Mobile Developer with experience in React Native, Flutter, and native iOS/Android development.
            Built cross-platform mobile applications using modern frameworks and tools.
            Skills: React Native, Flutter, Swift, Kotlin, Xcode, Android Studio, Firebase
            Tools: CocoaPods, Gradle, Fastlane, App Center, TestFlight
            """
        },
        {
            "name": "Simple Text with Abbreviations",
            "text": """
            Developer with experience in JS, TS, Py, and SQL. Worked with React, Node.js, and MongoDB.
            Used AWS, Docker, and K8s for deployment. Familiar with CI/CD and REST APIs.
            """
        }
    ]
    
    print("🧪 Testing Intelligent Skill Extraction\n")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Extract skills
        skills = skill_extractor.extract_skills(test_case['text'])
        
        print(f"📊 Extracted {len(skills)} skills:")
        for j, skill in enumerate(skills, 1):
            print(f"   {j:2d}. {skill}")
        
        print(f"\n📄 Original text preview: {test_case['text'][:100]}...")
    
    # Test skill categories
    print("\n" + "=" * 60)
    print("📚 Available Skill Categories:")
    print("-" * 40)
    
    categories = skill_extractor.get_skill_categories()
    for category, skills_list in categories.items():
        print(f"\n🔹 {category.replace('_', ' ').title()} ({len(skills_list)} skills):")
        # Show first 5 skills in each category
        for skill in skills_list[:5]:
            print(f"   • {skill}")
        if len(skills_list) > 5:
            print(f"   ... and {len(skills_list) - 5} more")
    
    print(f"\n🎯 Total unique skills available: {len(skill_extractor.all_skills)}")

if __name__ == "__main__":
    test_skill_extraction() 