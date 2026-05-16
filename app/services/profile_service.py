from app.models.user import User, Profile
from app.extensions import db
from app.utils.resume_parser import ResumeParser
from app.services.ai_service import AIService
import os
from flask import current_app

class ProfileService:
    @staticmethod
    def upload_resume(user_id, file):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None, "Profile not found"

        filename = f"resume_{user_id}_{file.filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        file.save(upload_path)
        
        # Parse resume text
        text = ResumeParser.extract_text(upload_path)
        clean_text = ResumeParser.clean_text(text)
        
        # Extract skills automatically
        skills = AIService.extract_skills(clean_text)
        
        # Update profile
        profile.resume_path = filename
        profile.resume_text = clean_text
        profile.skills = skills
        
        db.session.commit()
        return profile, None

    @staticmethod
    def update_profile(user_id, **kwargs):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            db.session.commit()
        return profile
