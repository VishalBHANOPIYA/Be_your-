from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
from sqlalchemy import JSON

# Use JSONB for Postgres, JSON for others (like SQLite in tests)
CompatibleJSON = JSON().with_variant(db.JSON(), 'postgresql')

class UserSprintSubmission(db.Model):
    __tablename__ = 'user_sprint_submissions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sprint_date = db.Column(db.Date, nullable=False)
    challenge_title = db.Column(db.String(255), nullable=False)
    challenge_type = db.Column(db.String(50), nullable=False) # 'debug', 'interview', 'design'
    challenge_data = db.Column(CompatibleJSON, nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, default=False)
    ai_feedback = db.Column(db.Text)
    xp_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Establish unique constraint to ensure only 1 submission per day per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'sprint_date', name='uq_user_sprint_date'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "sprint_date": self.sprint_date.isoformat() if self.sprint_date else None,
            "challenge_title": self.challenge_title,
            "challenge_type": self.challenge_type,
            "is_correct": self.is_correct,
            "xp_earned": self.xp_earned,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
