from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.ai_service import AIService
from app.models.code_challenge import CodeChallenge
from app.extensions import db
from datetime import datetime

playground_bp = Blueprint('playground', __name__)

@playground_bp.route('/playground')
@login_required
def dashboard():
    challenges = CodeChallenge.query.filter_by(user_id=current_user.id).order_by(CodeChallenge.created_at.desc()).all()
    return render_template('user/playground_dashboard.html', challenges=challenges)

@playground_bp.route('/playground/new')
@login_required
def new_challenge():
    user_skills = current_user.profile.skills if current_user.profile else []
    challenge_data = AIService.generate_code_challenge(user_skills)
    
    challenge = CodeChallenge(
        user_id=current_user.id,
        title=challenge_data['title'],
        problem_statement=challenge_data['problem'],
        starter_code=challenge_data['starter'],
        difficulty=challenge_data['difficulty']
    )
    db.session.add(challenge)
    db.session.commit()
    
    return redirect(url_for('playground.solve', challenge_id=challenge.id))

@playground_bp.route('/playground/solve/<uuid:challenge_id>')
@login_required
def solve(challenge_id):
    challenge = CodeChallenge.query.get_or_404(challenge_id)
    if challenge.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for('playground.dashboard'))
        
    return render_template('user/playground.html', challenge=challenge)

@playground_bp.route('/playground/submit/<uuid:challenge_id>', methods=['POST'])
@login_required
def submit(challenge_id):
    challenge = CodeChallenge.query.get_or_404(challenge_id)
    code = request.json.get('code')
    
    if not code:
        return jsonify({"success": False, "error": "No code submitted"})
        
    # Analyze code via AI
    analysis = AIService.analyze_code_solution(challenge.problem_statement, code)
    
    challenge.user_code = code
    challenge.score = analysis['score']
    challenge.feedback = analysis
    challenge.status = 'solved' if analysis['score'] > 70 else 'failed'
    challenge.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "analysis": analysis
    })
