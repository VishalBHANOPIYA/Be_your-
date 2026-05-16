from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.services.job_service import JobService
from app.utils.decorators import role_required
from app.models.job import Job
from app.models.application import Application
from app.extensions import db
from datetime import datetime

recruiter_bp = Blueprint('recruiter', __name__)

@recruiter_bp.route('/dashboard')
@login_required
@role_required('recruiter')
def dashboard():
    if not current_user.company:
        flash('Please set up your company profile first.', 'info')
        return redirect(url_for('recruiter.setup_company'))
    
    jobs = Job.query.filter_by(company_id=current_user.company.id).all()
    recent_apps = db.session.query(Application, Job)\
        .join(Job, Application.job_id == Job.id)\
        .filter(Job.company_id == current_user.company.id)\
        .order_by(Application.applied_at.desc())\
        .limit(5).all()
        
    return render_template('recruiter/dashboard.html', jobs=jobs, recent_applications=recent_apps)

@recruiter_bp.route('/jobs/post', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def post_job():
    if request.method == 'POST':
        data = request.form
        deadline = datetime.strptime(data.get('deadline'), '%Y-%m-%d') if data.get('deadline') else None
        
        JobService.create_job(
            company_id=current_user.company.id,
            title=data.get('title'),
            description=data.get('description'),
            skills_required=data.get('skills_required'),
            experience_min=data.get('experience_min', 0),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            location=data.get('location'),
            job_type=data.get('job_type', 'full-time'),
            deadline=deadline
        )
        flash('Job posted successfully!', 'success')
        return redirect(url_for('recruiter.dashboard'))
    return render_template('recruiter/post_job.html')

@recruiter_bp.route('/jobs/<uuid:job_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.company_id != current_user.company.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
        
    if request.method == 'POST':
        data = request.form
        deadline = datetime.strptime(data.get('deadline'), '%Y-%m-%d') if data.get('deadline') else None
        
        JobService.update_job(
            job_id,
            title=data.get('title'),
            description=data.get('description'),
            skills_required=data.get('skills_required'),
            experience_min=data.get('experience_min'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            location=data.get('location'),
            job_type=data.get('job_type'),
            deadline=deadline
        )
        flash('Job updated successfully!', 'success')
        return redirect(url_for('recruiter.dashboard'))
        
    return render_template('recruiter/post_job.html', job=job)

@recruiter_bp.route('/jobs/<uuid:job_id>/delete', methods=['POST'])
@login_required
@role_required('recruiter')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.company_id == current_user.company.id:
        JobService.delete_job(job_id)
        flash('Job deleted successfully.', 'success')
    return redirect(url_for('recruiter.dashboard'))

@recruiter_bp.route('/jobs/<uuid:job_id>/applicants')
@login_required
@role_required('recruiter')
def view_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    if job.company_id != current_user.company.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
        
    applicants = JobService.get_applicants_for_job(job_id)
    return render_template('recruiter/applicants.html', job=job, applicants=applicants)

@recruiter_bp.route('/application/<uuid:app_id>/status', methods=['POST'])
@login_required
@role_required('recruiter')
def update_app_status(app_id):
    status = request.form.get('status')
    JobService.update_application_status(app_id, status)
    flash(f'Application status updated to {status}.', 'success')
    return redirect(request.referrer or url_for('recruiter.dashboard'))

@recruiter_bp.route('/setup-company', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def setup_company():
    from app.models.job import Company
    if current_user.company:
        return redirect(url_for('recruiter.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        website = request.form.get('website')
        location = request.form.get('location')
        
        company = Company(
            name=name,
            description=description,
            website=website,
            location=location,
            recruiter_id=current_user.id
        )
        db.session.add(company)
        db.session.commit()
        flash('Company profile created! You can now post jobs.', 'success')
        return redirect(url_for('recruiter.dashboard'))
        
    return render_template('recruiter/setup_company.html')
