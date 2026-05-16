from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
from sqlalchemy import JSON

# Use JSONB for Postgres, JSON for others
CompatibleJSON = JSON().with_variant(db.JSON(), 'postgresql')

class CodeChallenge(db.Model):
    __tablename__ = 'code_challenges'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default='python')
    difficulty = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard
    
    starter_code = db.Column(db.Text)
    user_code = db.Column(db.Text)
    
    # AI Feedback and Scoring
    score = db.Column(db.Integer)
    feedback = db.Column(CompatibleJSON) # { "suggestions": [], "quality_metrics": {} }
    
    status = db.Column(db.String(20), default='pending') # pending, solved, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "problem": self.problem_statement,
            "language": self.language,
            "difficulty": self.difficulty,
            "starter_code": self.starter_code,
            "score": self.score,
            "status": self.status
        }
