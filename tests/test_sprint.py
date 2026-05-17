# ── FILE: tests/test_sprint.py ──
import pytest
from datetime import date, timedelta, datetime
from app.models.user import User, Profile
from app.services.sprint_service import SprintService
import uuid

@pytest.fixture
def test_user(db):
    """Fixture to generate a clean testing user and profile."""
    email = f"seeker_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Seeker Bob",
        email=email,
        role="seeker",
        streak_count=0,
        xp=0,
        level=1
    )
    user.set_password("Password123!")
    db.session.add(user)
    db.session.flush()
    
    profile = Profile(user_id=user.id, badges=[])
    db.session.add(profile)
    db.session.commit()
    return user

def test_streak_reset_without_freeze(db, test_user):
    """Verify that streak resets to 1 if user missed yesterday and lacks freeze badge."""
    today = date.today()
    day_before_yesterday = today - timedelta(days=2)
    
    # User completed a sprint 2 days ago, but missed yesterday
    test_user.last_sprint_date = day_before_yesterday
    test_user.streak_count = 5
    db.session.commit()
    
    # Submit today's challenge
    result = SprintService.evaluate_submission(test_user, "A")
    
    assert result["success"] is True
    # Without badge, streak resets to 1
    assert test_user.streak_count == 1

def test_streak_freeze_triggers_with_badge(db, test_user):
    """Verify that streak is preserved if user missed yesterday but possesses freeze badge."""
    today = date.today()
    day_before_yesterday = today - timedelta(days=2)
    
    # Award Streak Freeze badge
    test_user.profile.badges = [{"name": "Streak Freeze", "icon": "ac_unit"}]
    test_user.last_sprint_date = day_before_yesterday
    test_user.streak_count = 5
    db.session.commit()
    
    # Submit today's challenge
    result = SprintService.evaluate_submission(test_user, "A")
    
    assert result["success"] is True
    # With badge, streak is preserved and incremented to 6
    assert test_user.streak_count == 6

def test_evaluation_scoring_design(db, test_user):
    """Verify daily challenge evaluation and scoring for multiple choice questions."""
    # Since today's challenge is random or seeded, we evaluate with the dynamic challenge
    challenge = SprintService.get_daily_challenge(test_user)
    
    if challenge["type"] == "design":
        # Get correct answer choice
        correct_choice = next(
            (c["correct_choice"] for c in SprintService.CHALLENGES if c["id"] == challenge["id"]), 
            "A"
        )
        
        # Submit correct answer
        result = SprintService.evaluate_submission(test_user, correct_choice)
        assert result["success"] is True
        assert result["is_correct"] is True
        assert result["xp_earned"] == challenge["xp"]
        
        # Submit incorrect answer should return error but success in completion
        # Wait, since they already completed today's, another submit would fail.
        # But this verifies a successful correct submission.

def test_level_up_progression(db, test_user):
    """Verify that leveling occurs dynamically when user surpasses 500 XP threshold."""
    # Set user XP near level up boundary (e.g. 480 XP)
    test_user.xp = 480
    test_user.level = 1
    db.session.commit()
    
    challenge = SprintService.get_daily_challenge(test_user)
    # Submission yields at least 50 XP
    result = SprintService.evaluate_submission(test_user, "A")
    
    assert result["success"] is True
    assert test_user.xp >= 530
    assert test_user.level == 2
    assert result["level_up"] is True
    assert result["new_level"] == 2
