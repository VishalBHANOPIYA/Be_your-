import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.job import Job

class AIService:
    COMMON_SKILLS = [
        "Python", "Java", "Javascript", "C++", "C#", "Ruby", "PHP", "Go", "Rust", "Swift",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring", "Laravel",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
        "SQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow",
        "Data Science", "Data Analysis", "Pandas", "NumPy", "Scikit-Learn",
        "Project Management", "Agile", "Scrum", "Git", "System Design"
    ]

    @staticmethod
    def extract_skills(text):
        if not text: return []
        found_skills = []
        text_lower = text.lower()
        for skill in AIService.COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        return list(set(found_skills))

    @staticmethod
    def calculate_match_score(resume_text, job_description):
        if not resume_text or not job_description:
            return 0
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score), 2)

    @staticmethod
    def generate_roadmap(target_role, current_skills):
        # High-quality placeholder for AI Roadmap (Simulating GPT response)
        phases = [
            {
                "title": "Foundation & Core Skills",
                "milestones": [
                    {"name": "Master Core Language", "description": f"Deep dive into the primary language for {target_role}."},
                    {"name": "Data Structures & Algorithms", "description": "Crucial for interviews and efficient coding."}
                ]
            },
            {
                "title": "Domain Expertise",
                "milestones": [
                    {"name": "Framework Specialization", "description": f"Learn the industry-standard frameworks for {target_role}."},
                    {"name": "Database Management", "description": "Master SQL and NoSQL design patterns."}
                ]
            },
            {
                "title": "Advanced Engineering",
                "milestones": [
                    {"name": "System Design", "description": "Scaling applications and architectural patterns."},
                    {"name": "Cloud & DevOps", "description": "Deploying and managing infrastructure."}
                ]
            }
        ]
        return phases

    @staticmethod
    def get_job_recommendations(user_profile):
        resume_text = user_profile.resume_text or ""
        skills = user_profile.skills or []
        
        all_jobs = Job.query.filter_by(is_active=True).all()
        recommendations = []
        
        for job in all_jobs:
            # Score based on skills and description
            skill_match = len(set(skills) & set(job.skills_required)) / len(job.skills_required) if job.skills_required else 0
            semantic_score = AIService.calculate_match_score(resume_text, job.description)
            
            final_score = (skill_match * 0.4) + (semantic_score * 0.6)
            
            if final_score > 0.1: # Only suggest relevant ones
                recommendations.append({
                    "job": job,
                    "score": round(final_score * 100, 1)
                })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]
