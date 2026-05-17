from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.sprint_service import SprintService
from app.models.sprint import UserSprintSubmission
from datetime import date, timedelta

sprint_bp = Blueprint('sprint', __name__)

@sprint_bp.route('/')
@login_required
def dashboard():
    # 1. Reset streak if the user missed a day
    SprintService.check_and_reset_streaks(current_user)
    
    # 2. Get today's challenge
    challenge = SprintService.get_daily_challenge(current_user)
    
    # 3. Get leaderboard
    leaderboard = SprintService.get_leaderboard()
    
    # 4. Generate last 30 days completion history for the grid
    today = date.today()
    calendar_grid = []
    
    # Fetch all submissions for this user in the last 30 days
    start_date = today - timedelta(days=29)
    submissions = UserSprintSubmission.query.filter(
        UserSprintSubmission.user_id == current_user.id,
        UserSprintSubmission.sprint_date >= start_date
    ).all()
    
    completed_dates = {s.sprint_date for s in submissions}
    
    for i in range(30):
        d = start_date + timedelta(days=i)
        is_today = (d == today)
        is_future = (d > today)
        is_completed = (d in completed_dates)
        
        calendar_grid.append({
            "date_str": d.strftime("%b %d"),
            "is_today": is_today,
            "is_future": is_future,
            "is_completed": is_completed,
            "label": d.strftime("%d")
        })
        
    # Calculate progress percentage to next level (500 XP per level)
    xp_in_level = current_user.xp % 500
    level_progress = int((xp_in_level / 500) * 100)
    
    return render_template(
        'user/sprint.html',
        challenge=challenge,
        leaderboard=leaderboard,
        calendar_grid=calendar_grid,
        level_progress=level_progress,
        xp_in_level=xp_in_level
    )

@sprint_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    answer = request.form.get('answer', '')
    if not answer:
        return jsonify({"success": False, "message": "Answer cannot be empty!"}), 400
        
    result = SprintService.evaluate_submission(current_user, answer)
    if result.get('success'):
        return jsonify({
            "success": True,
            "is_correct": result.get("is_correct"),
            "feedback": result.get("ai_feedback"),
            "streak": result.get("new_streak"),
            "total_xp": result.get("new_xp"),
            "xp_earned": result.get("xp_earned"),
            "new_level": result.get("new_level"),
            "level_up": result.get("level_up")
        })
    return jsonify(result)

@sprint_bp.route('/history')
@login_required
def history():
    submissions = UserSprintSubmission.query.filter_by(user_id=current_user.id)\
        .order_by(UserSprintSubmission.sprint_date.desc()).all()
    
    total_completed = len(submissions)
    correct_count = sum(1 for s in submissions if s.is_correct)
    accuracy_pct = int((correct_count / total_completed * 100)) if total_completed > 0 else 0
    total_xp_earned = sum(s.xp_earned for s in submissions)
    
    return render_template(
        'user/sprint_history.html',
        submissions=submissions,
        total_completed=total_completed,
        correct_count=correct_count,
        accuracy_pct=accuracy_pct,
        total_xp_earned=total_xp_earned
    )

