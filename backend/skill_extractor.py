"""
Intelligent Skill Extraction from Resume Text
Uses multiple approaches to identify technical skills, tools, and technologies
"""

import re
from typing import List, Set, Dict
from collections import Counter

class SkillExtractor:
    def __init__(self):
        # Comprehensive skill dictionaries organized by category
        self.skills_db = {
            # Programming Languages
            "programming_languages": {
                "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby", 
                "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "powershell", "sql", "html", 
                "css", "dart", "elixir", "clojure", "haskell", "lua", "assembly", "cobol", "fortran"
            },
            
            # Web Technologies
            "web_technologies": {
                "react", "vue", "angular", "node.js", "express", "django", "flask", "spring", "asp.net", 
                "laravel", "rails", "fastapi", "gin", "echo", "koa", "hapi", "meteor", "ember", "svelte",
                "next.js", "nuxt.js", "gatsby", "jquery", "bootstrap", "tailwind", "sass", "less", "webpack",
                "vite", "rollup", "parcel", "babel", "eslint", "prettier", "jest", "cypress", "selenium"
            },
            
            # Databases
            "databases": {
                "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", 
                "oracle", "sql server", "sqlite", "neo4j", "influxdb", "couchdb", "firebase", "supabase",
                "cockroachdb", "timescaledb", "mariadb", "db2", "sybase"
            },
            
            # Cloud & DevOps
            "cloud_devops": {
                "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab ci", "github actions",
                "terraform", "ansible", "chef", "puppet", "prometheus", "grafana", "elk stack", "splunk",
                "datadog", "new relic", "cloudwatch", "stackdriver", "vault", "consul", "nomad"
            },
            
            # Data Science & ML
            "data_science_ml": {
                "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "matplotlib", 
                "seaborn", "plotly", "jupyter", "spark", "hadoop", "hive", "pig", "kafka", "airflow",
                "mlflow", "kubeflow", "sagemaker", "vertex ai", "azure ml", "tableau", "power bi",
                "looker", "dbt", "snowflake", "databricks", "rapids", "xgboost", "lightgbm"
            },
            
            # Mobile Development
            "mobile_development": {
                "react native", "flutter", "xamarin", "ionic", "cordova", "phonegap", "swift", 
                "objective-c", "kotlin", "java", "xcode", "android studio", "firebase", "onesignal",
                "cocoa pods", "gradle", "maven", "fastlane", "app center", "testflight"
            },
            
            # Tools & Platforms
            "tools_platforms": {
                "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack", "teams", 
                "zoom", "figma", "sketch", "adobe xd", "invision", "postman", "insomnia", "swagger",
                "openapi", "graphql", "rest api", "soap", "grpc", "websocket", "oauth", "jwt"
            },
            
            # Operating Systems
            "operating_systems": {
                "linux", "ubuntu", "centos", "debian", "red hat", "windows", "macos", "unix", 
                "freebsd", "openbsd", "solaris", "aix", "hp-ux"
            },
            
            # Networking & Security
            "networking_security": {
                "tcp/ip", "dns", "http", "https", "ssl", "tls", "vpn", "firewall", "load balancer",
                "nginx", "apache", "cisco", "juniper", "wireshark", "nmap", "metasploit", "burp suite",
                "penetration testing", "vulnerability assessment", "siem", "ids", "ips", "waf"
            },
            
            # Methodologies & Frameworks
            "methodologies": {
                "agile", "scrum", "kanban", "waterfall", "devops", "ci/cd", "tdd", "bdd", "ddd",
                "microservices", "serverless", "event-driven", "api-first", "design thinking",
                "lean", "six sigma", "itil", "cobit"
            }
        }
        
        # Create a flat set of all skills for quick lookup
        self.all_skills = set()
        for category_skills in self.skills_db.values():
            self.all_skills.update(category_skills)
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text using multiple approaches
        """
        if not text:
            return []
        
        text_lower = text.lower()
        extracted_skills = set()
        
        # Method 1: Direct keyword matching
        direct_matches = self._find_direct_matches(text_lower)
        extracted_skills.update(direct_matches)
        
        # Method 2: Pattern-based extraction
        pattern_matches = self._find_pattern_matches(text_lower)
        extracted_skills.update(pattern_matches)
        
        # Method 3: Context-based extraction
        context_matches = self._find_context_matches(text_lower)
        extracted_skills.update(context_matches)
        
        # Method 4: Abbreviation expansion
        abbreviation_matches = self._find_abbreviation_matches(text_lower)
        extracted_skills.update(abbreviation_matches)
        
        # Clean and normalize skills
        cleaned_skills = self._clean_and_normalize_skills(extracted_skills)
        
        # Sort by relevance (frequency in text)
        skill_frequency = self._calculate_skill_frequency(text_lower, cleaned_skills)
        sorted_skills = sorted(cleaned_skills, key=lambda x: skill_frequency.get(x, 0), reverse=True)
        
        return sorted_skills[:15]  # Return top 15 most relevant skills
    
    def _find_direct_matches(self, text: str) -> Set[str]:
        """Find direct keyword matches"""
        matches = set()
        for skill in self.all_skills:
            if skill in text:
                matches.add(skill)
        return matches
    
    def _find_pattern_matches(self, text: str) -> Set[str]:
        """Find skills using regex patterns"""
        matches = set()
        
        # Patterns for common skill mentions
        patterns = [
            r'\b(?:proficient in|experienced with|skilled in|expert in|knowledge of)\s+([a-zA-Z0-9\s+#]+?)(?:\s|,|\.|$)',
            r'\b(?:worked with|used|developed|built|implemented)\s+([a-zA-Z0-9\s+#]+?)(?:\s|,|\.|$)',
            r'\b(?:technologies?|tools?|frameworks?|languages?):\s*([a-zA-Z0-9\s,#]+)',
            r'\b(?:skills?|expertise):\s*([a-zA-Z0-9\s,#]+)',
        ]
        
        for pattern in patterns:
            found = re.findall(pattern, text)
            for match in found:
                # Clean the matched text
                cleaned = re.sub(r'[^\w\s+#]', '', match).strip()
                if cleaned in self.all_skills:
                    matches.add(cleaned)
        
        return matches
    
    def _find_context_matches(self, text: str) -> Set[str]:
        """Find skills based on context clues"""
        matches = set()
        
        # Context indicators
        context_indicators = [
            'programming', 'development', 'coding', 'software', 'web', 'mobile', 'data',
            'database', 'cloud', 'devops', 'testing', 'design', 'analysis'
        ]
        
        # Look for skills near context indicators
        for indicator in context_indicators:
            if indicator in text:
                # Find words near the indicator that might be skills
                words = text.split()
                for i, word in enumerate(words):
                    if indicator in word:
                        # Check surrounding words
                        for j in range(max(0, i-3), min(len(words), i+4)):
                            potential_skill = words[j].lower().strip('.,;:!?')
                            if potential_skill in self.all_skills:
                                matches.add(potential_skill)
        
        return matches
    
    def _find_abbreviation_matches(self, text: str) -> Set[str]:
        """Find skills from common abbreviations"""
        abbreviation_map = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'cpp': 'c++',
            'csharp': 'c#',
            'psql': 'postgresql',
            'my sql': 'mysql',
            'mongo': 'mongodb',
            'k8s': 'kubernetes',
            'k8': 'kubernetes',
            'tf': 'terraform',
            'aws s3': 'aws',
            'aws ec2': 'aws',
            'aws lambda': 'aws',
            'gcp cloud': 'gcp',
            'azure cloud': 'azure',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ui': 'user interface',
            'ux': 'user experience',
            'api': 'rest api',
            'db': 'database',
            'sql db': 'sql',
            'nosql': 'mongodb',
            'ci/cd': 'ci/cd',
            'cicd': 'ci/cd'
        }
        
        matches = set()
        for abbrev, full_name in abbreviation_map.items():
            if abbrev in text and full_name in self.all_skills:
                matches.add(full_name)
        
        return matches
    
    def _clean_and_normalize_skills(self, skills: Set[str]) -> Set[str]:
        """Clean and normalize extracted skills"""
        cleaned = set()
        
        for skill in skills:
            # Remove common prefixes/suffixes
            skill = re.sub(r'^(the\s+|a\s+|an\s+)', '', skill)
            skill = re.sub(r'(\s+and\s+|\s+or\s+|\s+&\s+)', ' ', skill)
            
            # Normalize common variations
            skill = skill.replace('javascript', 'javascript')
            skill = skill.replace('typescript', 'typescript')
            skill = skill.replace('python', 'python')
            skill = skill.replace('react.js', 'react')
            skill = skill.replace('reactjs', 'react')
            skill = skill.replace('node.js', 'node.js')
            skill = skill.replace('nodejs', 'node.js')
            
            # Remove extra whitespace
            skill = ' '.join(skill.split())
            
            if skill and len(skill) > 1:
                cleaned.add(skill)
        
        return cleaned
    
    def _calculate_skill_frequency(self, text: str, skills: Set[str]) -> Dict[str, int]:
        """Calculate frequency of skills in text"""
        frequency = {}
        for skill in skills:
            # Count occurrences (case insensitive)
            count = len(re.findall(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE))
            frequency[skill] = count
        return frequency
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """Get skills organized by category"""
        return {category: list(skills) for category, skills in self.skills_db.items()}
    
    def add_custom_skill(self, skill: str, category: str = "custom"):
        """Add a custom skill to the database"""
        if category not in self.skills_db:
            self.skills_db[category] = set()
        
        self.skills_db[category].add(skill.lower())
        self.all_skills.add(skill.lower())

# Global instance
skill_extractor = SkillExtractor() 