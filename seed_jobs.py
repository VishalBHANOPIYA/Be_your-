import uuid
from app import create_app
from app.extensions import db
from app.models.job import Job
from app.models.company import Company
from app.models.user import User

def seed_test_jobs():
    app = create_app()
    with app.app_context():
        # Get or create a test recruiter
        recruiter = User.query.filter_by(role='recruiter').first()
        if not recruiter:
            recruiter = User(
                name="Test Recruiter",
                email="recruiter@example.com",
                role="recruiter"
            )
            recruiter.set_password("password123")
            db.session.add(recruiter)
            db.session.commit()

        # Create a few companies
        companies = [
            {"name": "TechFlow Systems", "location": "Remote", "desc": "Leading cloud solutions provider."},
            {"name": "Quantum AI", "location": "New York, NY", "desc": "Next-gen machine learning research lab."},
            {"name": "Pixel Perfect", "location": "Austin, TX", "desc": "Design-first frontend agency."},
            {"name": "SecureNet", "location": "Washington, D.C.", "desc": "Cybersecurity and infrastructure experts."}
        ]
        
        company_objects = []
        for c_data in companies:
            comp = Company.query.filter_by(name=c_data['name']).first()
            if not comp:
                comp = Company(
                    name=c_data['name'],
                    location=c_data['location'],
                    description=c_data['desc'],
                    recruiter_id=recruiter.id
                )
                db.session.add(comp)
            company_objects.append(comp)
        
        db.session.commit()

        # Create diverse Jobs
        jobs_to_add = [
            {
                "title": "Senior Frontend Engineer",
                "company": company_objects[2],
                "location": "Remote",
                "salary_min": 130000,
                "salary_max": 190000,
                "type": "Full-time",
                "desc": "Build pixel-perfect React applications with focus on performance and accessibility. Experience with GSAP and Tailwind is a plus.",
                "skills": ["React", "Javascript", "Tailwind", "CSS", "GSAP"]
            },
            {
                "title": "Backend Python Developer",
                "company": company_objects[0],
                "location": "New York, NY",
                "salary_min": 120000,
                "salary_max": 175000,
                "type": "Full-time",
                "desc": "Join our backend team to build robust Flask and FastAPI services. Experience with PostgreSQL and Redis is essential.",
                "skills": ["Python", "Flask", "PostgreSQL", "Redis", "SQLAlchemy"]
            },
            {
                "title": "ML / AI Researcher",
                "company": company_objects[1],
                "location": "New York, NY",
                "salary_min": 150000,
                "salary_max": 250000,
                "type": "Full-time",
                "desc": "Work on cutting-edge LLM fine-tuning and computer vision models. PyTorch experience required.",
                "skills": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "NLP"]
            },
            {
                "title": "DevOps Architect",
                "company": company_objects[3],
                "location": "Remote",
                "salary_min": 140000,
                "salary_max": 210000,
                "type": "Contract",
                "desc": "Help us modernize our infrastructure using Kubernetes and Terraform. Focus on security and CI/CD automation.",
                "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD"]
            },
            {
                "title": "Product Designer (UI/UX)",
                "company": company_objects[2],
                "location": "Austin, TX",
                "salary_min": 100000,
                "salary_max": 150000,
                "type": "Full-time",
                "desc": "Design intuitive user journeys and high-fidelity mockups using Figma.",
                "skills": ["Figma", "Design", "Communication", "Agile"]
            }
        ]

        for j_data in jobs_to_add:
            existing_job = Job.query.filter_by(title=j_data['title'], company_id=j_data['company'].id).first()
            if not existing_job:
                job = Job(
                    title=j_data['title'],
                    company_id=j_data['company'].id,
                    location=j_data['location'],
                    salary_min=j_data['salary_min'],
                    salary_max=j_data['salary_max'],
                    job_type=j_data['type'],
                    description=j_data['desc'],
                    skills_required=j_data['skills'],
                    is_active=True
                )
                db.session.add(job)
        
        db.session.commit()
        print("Successfully seeded 5 diverse test jobs!")

if __name__ == "__main__":
    seed_test_jobs()
