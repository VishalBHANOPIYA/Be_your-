import uuid
from app import create_app
from app.extensions import db
from app.models.user import User, Profile
from app.models.company import Company
from app.models.job import Job
from datetime import datetime, timedelta

def seed_data():
    app = create_app()
    with app.app_context():
        # Create a recruiter
        recruiter = User(name="Sarah Recruiter", email="recruiter@example.com", role='recruiter')
        recruiter.set_password("password123")
        db.session.add(recruiter)
        db.session.flush()

        # Create a seeker
        seeker = User(name="John Seeker", email="seeker@example.com", role='seeker')
        seeker.set_password("password123")
        db.session.add(seeker)
        db.session.flush()

        # Create profiles
        recruiter_profile = Profile(user_id=recruiter.id)
        seeker_profile = Profile(user_id=seeker.id, headline="Aspiring Full Stack Developer", skills=["Python", "Flask", "Tailwind CSS"])
        db.session.add(recruiter_profile)
        db.session.add(seeker_profile)

        # Create a company
        company = Company(
            name="NeuralPath AI",
            description="Leading the way in neural architecture and AI-driven career development.",
            website="https://neuralpath.ai",
            location="San Francisco, CA",
            recruiter_id=recruiter.id
        )
        db.session.add(company)
        db.session.flush()

        # Create some jobs
        jobs = [
            Job(
                company_id=company.id,
                title="Senior AI Engineer",
                description="Join our elite team to build the next generation of neural modeling tools.\n- Design and implement scalable AI pipelines.\n- Collaborate with product and design teams.",
                skills_required=["PyTorch", "Transformers", "Distributed Systems"],
                experience_min=5,
                salary_min=150000,
                salary_max=250000,
                location="Remote / San Francisco",
                job_type="full-time",
                deadline=datetime.utcnow() + timedelta(days=30)
            ),
            Job(
                company_id=company.id,
                title="Full Stack Developer (Flask/React)",
                description="Looking for a versatile developer to help us scale our platform.\n- Build robust backend APIs with Flask.\n- Craft premium UI experiences with Tailwind and React.",
                skills_required=["Flask", "PostgreSQL", "React", "Tailwind"],
                experience_min=3,
                salary_min=120000,
                salary_max=180000,
                location="San Francisco, CA",
                job_type="full-time",
                deadline=datetime.utcnow() + timedelta(days=20)
            )
        ]
        db.session.add_all(jobs)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
