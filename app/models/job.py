from datetime import datetime
import uuid
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

CompatibleJSON = JSON().with_variant(JSONB(), 'postgresql')

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(CompatibleJSON) # ["Python", "Django"]
    experience_min = db.Column(db.Integer)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    location = db.Column(db.String(120))
    job_type = db.Column(db.String(50), default='full-time')
    is_active = db.Column(db.Boolean, default=True)
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='job', lazy=True)

    @property
    def days_left(self):
        if not self.deadline:
            return None
        deadline_dt = self.deadline
        if not isinstance(deadline_dt, datetime):
            from datetime import date
            if isinstance(deadline_dt, date):
                deadline_dt = datetime.combine(deadline_dt, datetime.min.time())
        delta = deadline_dt - datetime.utcnow()
        return max(0, delta.days)
