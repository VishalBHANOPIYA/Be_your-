from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.services.job_service import JobService
from app.extensions import db

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/')
def list_jobs():
    query = request.args.get('q', '')
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
        'location': location,
        'job_type': request.args.get('job_type', '')
    }
        
    return render_template('jobs/list.html', pagination=pagination, filters=filters, saved_job_ids=saved_job_ids)

@jobs_bp.route('/<uuid:job_id>')
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    is_saved = False
    if current_user.is_authenticated:
        is_saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job_id).first() is not None
    return render_template('jobs/view.html', job=job, is_saved=is_saved)

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
