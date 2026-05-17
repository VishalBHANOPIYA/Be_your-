from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.services.interview_service import InterviewService
from app.services.ai_service import AIService
from app.models.interview import Interview
from app.models.job import Job
import uuid

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/interview/start', methods=['GET', 'POST'])
@login_required
def start_interview():
    if request.method == 'POST':
        category = request.form.get('category', 'technical')
        job_role = request.form.get('job_role', 'Software Engineer')
        specific_skill = request.form.get('specific_skill')
        
        # Prioritize specific skill if provided
        final_role = specific_skill if specific_skill else job_role
        
        interview = InterviewService.start_session(current_user.id, final_role, category)
        return redirect(url_for('ai.interview_session', interview_id=interview.id))
        
    return render_template('ai/interview_setup.html')

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

@ai_bp.route('/cover-letter/generate', methods=['POST'])
@login_required
def generate_cover_letter():
    data = request.json or {}
    job_id_str = data.get('job_id')
    
    if not job_id_str:
        return jsonify({"success": False, "error": "Job ID is required."}), 400
        
    try:
        job_id = uuid.UUID(job_id_str)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid Job ID format."}), 400
        
    job = Job.query.get_or_404(job_id)
    
    if not current_user.profile:
        return jsonify({"success": False, "error": "Please complete your profile (upload resume) first."}), 400
        
    letter = AIService.generate_cover_letter(current_user.profile, job)
    return jsonify({"success": True, "letter": letter})

@ai_bp.route('/outreach', methods=['GET'])
@login_required
def outreach_workspace():
    # Pre-fill options from URL query params (e.g. from Job Detail page)
    job_id_str = request.args.get('job_id')
    prefill_job = None
    if job_id_str:
        try:
            job_id = uuid.UUID(job_id_str)
            prefill_job = Job.query.get(job_id)
        except (ValueError, TypeError):
            pass

    return render_template('ai/outreach.html', prefill_job=prefill_job)

@ai_bp.route('/outreach/generate', methods=['POST'])
@login_required
def generate_outreach():
    data = request.json or {}
    job_title = data.get('job_title', '').strip()
    company_name = data.get('company_name', '').strip()
    job_description = data.get('job_description', '').strip()
    tone = data.get('tone', 'professional').strip()
    manual_skills_str = data.get('skills', '').strip()

    if not job_title or not company_name:
        return jsonify({"success": False, "error": "Job Title and Company Name are required."}), 400

    manual_skills = []
    if manual_skills_str:
        manual_skills = [s.strip() for s in manual_skills_str.split(',') if s.strip()]

    profile = current_user.profile if current_user.is_authenticated else None
    
    try:
        outreach_data = AIService.generate_outreach_copy(
            user_profile=profile,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            tone=tone,
            manual_skills=manual_skills
        )
        return jsonify({
            "success": True,
            "cover_letter": outreach_data["cover_letter"],
            "cold_email_subject": outreach_data["cold_email_subject"],
            "cold_email_body": outreach_data["cold_email_body"],
            "linkedin_message": outreach_data["linkedin_message"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

