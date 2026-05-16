from app.extensions import db
from datetime import datetime

class BadgeService:
    @staticmethod
    def award_badge(user, name, level="Gold", icon="verified", source="AI Analysis"):
        """Award a badge to a user if they don't already have it."""
        if not user.profile:
            return False
            
        badges = list(user.profile.badges) if user.profile.badges else []
        
        # Check if already earned
        if any(b['name'] == name for b in badges):
            return False
            
        new_badge = {
            "name": name,
            "level": level,
            "icon": icon,
            "source": source,
            "earned_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        badges.append(new_badge)
        user.profile.badges = badges
        db.session.commit()
        return True

    @staticmethod
    def check_and_award_interview_badge(user, score, role):
        """Check if interview score warrants a badge."""
        if score >= 80:
            badge_name = f"AI Verified: {role} Expert"
            return BadgeService.award_badge(
                user, 
                badge_name, 
                level="Elite", 
                icon="military_tech", 
                source="Mock Interview"
            )
        return False

    @staticmethod
    def check_and_award_portfolio_badge(user, score):
        """Check if portfolio/resume score warrants a badge."""
        if score >= 90:
            return BadgeService.award_badge(
                user, 
                "ATS Master: Top 1% Portfolio", 
                level="Gold", 
                icon="workspace_premium", 
                source="Portfolio Optimizer"
            )
        return False
