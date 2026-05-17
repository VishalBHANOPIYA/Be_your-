from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.models.application import Application
from app.services.job_service import JobService
from app.services.ai_service import AIService
from app.extensions import db

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/')
def list_jobs():
    query = request.args.get('q') or request.args.get('title') or ''
    location = request.args.get('location', '')
    
    jobs_query = Job.query.filter_by(is_active=True)
    
    if query:
        jobs_query = jobs_query.filter(Job.title.ilike(f'%{query}%'))
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f'%{location}%'))
        
    page = request.args.get('page', 1, type=int)
    pagination = jobs_query.order_by(Job.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # Get IDs of saved jobs if user is logged in
    saved_job_ids = []
    if current_user.is_authenticated:
        saved_job_ids = [s.job_id for s in SavedJob.query.filter_by(user_id=current_user.id).all()]
        
    filters = {
        'q': query,
        'title': query,
        'location': location,
        'job_type': request.args.get('job_type', '')
    }
        
    return render_template('jobs/list.html', pagination=pagination, filters=filters, saved_job_ids=saved_job_ids)

@jobs_bp.route('/<uuid:job_id>')
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    is_saved = False
    skill_gap = None
    
    if current_user.is_authenticated:
        is_saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job_id).first() is not None
        if current_user.profile:
            skill_gap = AIService.get_skill_gap_data(current_user.profile, job)
            
    return render_template('jobs/detail.html', job=job, is_saved=is_saved, skill_gap=skill_gap)

@jobs_bp.route('/<uuid:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    # 1. @login_required handled by decorator
    
    # 2. Role check
    if current_user.role != 'seeker':
        flash("Recruiters cannot apply for jobs.", "warning")
        return redirect(url_for('jobs.list_jobs'))
        
    # 3. Check if already applied
    existing = Application.query.filter_by(
        user_id=current_user.id, job_id=job_id).first()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for('jobs.view_job', job_id=job_id))
        
    # 4. Get job
    job = Job.query.get_or_404(job_id)
    
    # 5. Check resume uploaded
    if not current_user.profile or not current_user.profile.resume_text:
        flash("Please upload your resume before applying.", "warning")
        return redirect(url_for('user.dashboard'))
        
    # 6. AI scoring (Inline logic as requested)
    resume_text = current_user.profile.resume_text
    job_skills = job.skills_required or []
    user_skills = AIService.extract_skills(resume_text)
    
    matched = list(set(user_skills) & set(job_skills))
    missing = [s for s in job_skills if s not in user_skills]
    score = (len(matched)/len(job_skills)*100) if job_skills else 50.0
    result = {'score': round(score, 1), 'matched_skills': matched, 'missing_skills': missing}
    
    # 7. Create Application
    app_record = Application(
        user_id=current_user.id,
        job_id=job_id,
        resume_score=result['score'],
        matched_skills=result['matched_skills'],
        missing_skills=result['missing_skills'],
        status='applied'
    )
    db.session.add(app_record)
    db.session.commit()
    
    from app.utils.notify import send_notification
    send_notification(current_user.id,
      f"✅ You applied to '{job.title}'. Match score: {result['score']}%")
    
    # 8. Flash success
    flash(f"Applied successfully! Your match score: {result['score']}%", "success")
    
    # 9. Redirect
    return redirect(url_for('user.dashboard'))

@jobs_bp.route('/<uuid:job_id>/save', methods=['POST'])
@login_required
def save_job(job_id):
    if JobService.save_job(current_user.id, job_id):
        flash('Job saved to your bookmarks!', 'success')
    return redirect(request.referrer or url_for('jobs.list_jobs'))

@jobs_bp.route('/<uuid:job_id>/unsave', methods=['POST'])
@login_required
def unsave_job(job_id):
    if JobService.unsave_job(current_user.id, job_id):
        flash('Job removed from bookmarks.', 'info')
    return redirect(request.referrer or url_for('jobs.list_jobs'))
