from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(UUID(as_uuid=True), db.ForeignKey('jobs.id'), nullable=False)
    resume_score = db.Column(db.Float)
    matched_skills = db.Column(JSONB)
    missing_skills = db.Column(JSONB)
    status = db.Column(db.Enum('applied', 'viewed', 'shortlisted', 'rejected', 'hired', name='application_status'), default='applied')
    cover_note = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
