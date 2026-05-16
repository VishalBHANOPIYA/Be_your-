from datetime import datetime
import uuid
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

CompatibleJSON = JSON().with_variant(JSONB(), 'postgresql')

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    job_role = db.Column(db.String(120))
    category = db.Column(db.String(50), default='technical') # technical, behavioral, hr
    questions = db.Column(CompatibleJSON) # List of questions: ["Q1", "Q2"]
    answers = db.Column(CompatibleJSON) # Dict: {"0": "Ans1", "1": "Ans2"}
    feedback = db.Column(CompatibleJSON) # Dict: {"0": "Feedback1"}
    status = db.Column(db.String(20), default='started') # started, completed
    total_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
