from app.models.job import Job
from app.models.saved_job import SavedJob
from app.models.application import Application
from app.models.user import User, Profile
from app.extensions import db
from datetime import datetime

class JobService:
    @staticmethod
    def create_job(company_id, title, description, skills_required, experience_min, salary_min, salary_max, location, job_type, deadline):
        # Convert skills_required from comma-separated string to list
        if isinstance(skills_required, str):
            skills_required = [s.strip() for s in skills_required.split(',') if s.strip()]
            
        job = Job(
            company_id=company_id,
            title=title,
            description=description,
            skills_required=skills_required,
            experience_min=experience_min,
            salary_min=salary_min,
            salary_max=salary_max,
            location=location,
            job_type=job_type,
            deadline=deadline,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def update_job(job_id, **kwargs):
        job = Job.query.get(job_id)
        if job:
            if 'skills_required' in kwargs and isinstance(kwargs['skills_required'], str):
                kwargs['skills_required'] = [s.strip() for s in kwargs['skills_required'].split(',') if s.strip()]
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            db.session.commit()
        return job

    @staticmethod
    def delete_job(job_id):
        job = Job.query.get(job_id)
        if job:
            job.is_active = False
            db.session.commit()
        return True

    @staticmethod
    def get_applicants_for_job(job_id):
        # Join with User and Profile to get complete candidate data
        applicants = db.session.query(Application, User, Profile)\
            .join(User, Application.user_id == User.id)\
            .join(Profile, User.id == Profile.user_id)\
            .filter(Application.job_id == job_id)\
            .all()
        
        # Mark all as viewed when recruiter fetches them
        for app, user, prof in applicants:
            if app.status == 'applied':
                app.status = 'viewed'
        db.session.commit()
        
        return applicants

    @staticmethod
    def update_application_status(application_id, status):
        app = Application.query.get(application_id)
        if app:
            app.status = status
            db.session.commit()
        return app

    @staticmethod
    def save_job(user_id, job_id):
        if not SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first():
            saved = SavedJob(user_id=user_id, job_id=job_id)
            db.session.add(saved)
            db.session.commit()
            return True
        return False

    @staticmethod
    def unsave_job(user_id, job_id):
        saved = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_saved_jobs(user_id):
        return db.session.query(Job).join(SavedJob, Job.id == SavedJob.job_id).filter(SavedJob.user_id == user_id).all()
