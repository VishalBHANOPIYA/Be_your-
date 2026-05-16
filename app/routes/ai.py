from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.services.interview_service import InterviewService
from app.services.ai_service import AIService
from app.models.interview import Interview

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/interview/start', methods=['GET', 'POST'])
@login_required
def start_interview():
    category = request.args.get('category', 'technical')
    job_role = request.args.get('job_role')
    
    interview = InterviewService.start_session(current_user.id, job_role, category)
    return redirect(url_for('ai.interview_session', interview_id=interview.id))

@ai_bp.route('/interview/<uuid:interview_id>')
@login_required
def interview_session(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id:
        flash('Unauthorized access to interview session.', 'danger')
        return redirect(url_for('user.dashboard'))
    return render_template('ai/interview.html', interview=interview)

@ai_bp.route('/interview/<uuid:interview_id>/submit', methods=['POST'])
@login_required
def submit_answer(interview_id):
    data = request.json
    question_index = data.get('index')
    answer_text = data.get('answer')
    interview, error = InterviewService.submit_answer(interview_id, question_index, answer_text)
    if error:
        return jsonify({"success": False, "error": error}), 400
    return jsonify({"success": True})

@ai_bp.route('/interview/<uuid:interview_id>/finish', methods=['POST'])
@login_required
def finish_interview(interview_id):
    InterviewService.finish_session(interview_id)
    return jsonify({"success": True, "redirect": url_for('ai.interview_analysis', interview_id=interview_id)})

@ai_bp.route('/interview/<uuid:interview_id>/analysis')
@login_required
def interview_analysis(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    return render_template('ai/analysis.html', interview=interview)

@ai_bp.route('/roadmap/generate', methods=['POST'])
@login_required
def generate_roadmap():
    target_role = request.form.get('target_role')
    current_skills = current_user.profile.skills or []
    
    roadmap_data = AIService.generate_roadmap(target_role, current_skills)
    return render_template('user/roadmap.html', roadmap=roadmap_data, target_role=target_role)

@ai_bp.route('/recommendations')
@login_required
def recommendations():
    recs = AIService.get_job_recommendations(current_user.profile)
    return jsonify({
        "success": True,
        "recommendations": [
            {
                "id": r['job'].id,
                "title": r['job'].title,
                "company": r['job'].company.name,
                "score": r['score'],
                "location": r['job'].location
            } for r in recs
        ]
    })
