from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.services.job_service import JobService
from app.utils.decorators import role_required
from app.models.job import Job
from app.models.application import Application
from app.extensions import db
from datetime import datetime
import re

recruiter_bp = Blueprint('recruiter', __name__)

def safe_parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # Handle custom case where year might have more than 4 digits (e.g. '62026-02-20')
    match = re.match(r'^(\d{4,5})-(\d{2})-(\d{2})', date_str)
    if match:
        year_str, month_str, day_str = match.groups()
        if len(year_str) > 4:
            year_str = year_str[-4:]
        try:
            return datetime(int(year_str), int(month_str), int(day_str))
        except ValueError:
            pass
            
    return None

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
        
    from sqlalchemy import func
    
    job_ids = [j.id for j in jobs]
    total_applicants = 0
    avg_score = 0
    job_app_counts = {}   # {job_id: count}
    
    if job_ids:
        total_applicants = Application.query.filter(
            Application.job_id.in_(job_ids)).count()
        
        avg = db.session.query(func.avg(Application.resume_score))\
            .filter(Application.job_id.in_(job_ids)).scalar()
        avg_score = round(avg, 1) if avg else 0
        
        # Per-job applicant count
        counts = db.session.query(
            Application.job_id, func.count(Application.id)
        ).filter(Application.job_id.in_(job_ids))\
         .group_by(Application.job_id).all()
        job_app_counts = {str(jid): c for jid, c in counts}
    
    return render_template('recruiter/dashboard.html',
        jobs=jobs, recent_applications=recent_apps,
        company=current_user.company,
        total_applicants=total_applicants,
        avg_score=avg_score,
        job_app_counts=job_app_counts)

@recruiter_bp.route('/jobs/post', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def post_job():
    if request.method == 'POST':
        data = request.form
        deadline = safe_parse_date(data.get('deadline'))
        
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
        deadline = safe_parse_date(data.get('deadline'))
        
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
    
    from app.utils.notify import send_notification
    from app.models.application import Application
    from app.utils.email import send_email
    from flask import url_for
    
    app_obj = Application.query.get(app_id)
    if app_obj:
        status_messages = {
            'shortlisted': f"🎉 Congratulations! You've been shortlisted for a position.",
            'rejected': f"Thank you for applying. Unfortunately, you were not selected this time.",
            'hired': f"🏆 Amazing news! You've been selected for the role!"
        }
        msg = status_messages.get(status)
        if msg:
            send_notification(app_obj.user_id, msg)
            
            # Send actual email notification
            user = app_obj.user
            job = app_obj.job
            dashboard_url = url_for('user.dashboard', _external=True)
            
            send_email(
                to=user.email,
                subject=f"Application Update: {job.title} at {job.company.name}",
                template='status_update',
                name=user.name,
                job_title=job.title,
                company_name=job.company.name,
                status=status.capitalize(),
                dashboard_url=dashboard_url
            )
            
    flash(f'Application status updated to {status}.', 'success')
    return redirect(request.referrer or url_for('recruiter.dashboard'))

@recruiter_bp.route('/setup-company', methods=['GET', 'POST'])
@login_required
@role_required('recruiter')
def setup_company():
    from app.models.company import Company
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

@recruiter_bp.route('/analytics')
@login_required
@role_required('recruiter')
def analytics():
    if not current_user.company:
        flash('Please set up your company profile first.', 'info')
        return redirect(url_for('recruiter.setup_company'))
    
    company_id = current_user.company.id
    
    from sqlalchemy import func
    from app.models.user import User
    
    total_jobs = Job.query.filter_by(company_id=company_id).count()
    active_jobs = Job.query.filter_by(company_id=company_id, is_active=True).count()
    
    total_apps = db.session.query(func.count(Application.id))\
        .join(Job).filter(Job.company_id == company_id).scalar() or 0
    
    avg = db.session.query(func.avg(Application.resume_score))\
        .join(Job).filter(Job.company_id == company_id).scalar()
    avg_score = round(avg, 1) if avg else 0
    
    shortlisted = db.session.query(func.count(Application.id))\
        .join(Job).filter(Job.company_id == company_id,
                          Application.status == 'shortlisted').scalar() or 0
    
    hired = db.session.query(func.count(Application.id))\
        .join(Job).filter(Job.company_id == company_id,
                          Application.status == 'hired').scalar() or 0
    
    # Bar chart data — applications per job
    jobs_with_apps = db.session.query(
        Job.title, func.count(Application.id).label('app_count')
    ).outerjoin(Application)\
     .filter(Job.company_id == company_id)\
     .group_by(Job.id, Job.title)\
     .order_by(func.count(Application.id).desc())\
     .limit(8).all()
    job_titles = [t[:25] + '...' if len(t) > 25 else t for t, _ in jobs_with_apps]
    job_app_counts = [c for _, c in jobs_with_apps]
    
    # Doughnut chart data — status breakdown
    status_counts = db.session.query(
        Application.status, func.count(Application.id)
    ).join(Job).filter(Job.company_id == company_id)\
     .group_by(Application.status).all()
    status_dict = {s: c for s, c in status_counts}
    
    # Top 5 applicants
    top_applicants = db.session.query(Application, User, Job)\
        .join(User, Application.user_id == User.id)\
        .join(Job, Application.job_id == Job.id)\
        .filter(Job.company_id == company_id)\
        .order_by(Application.resume_score.desc())\
        .limit(5).all()
    
    return render_template('recruiter/analytics.html',
        company=current_user.company,
        total_jobs=total_jobs, active_jobs=active_jobs,
        total_applications=total_apps, avg_score=avg_score,
        shortlisted=shortlisted, hired=hired,
        job_titles=job_titles, job_app_counts=job_app_counts,
        status_dict=status_dict, top_applicants=top_applicants)

@recruiter_bp.route('/applicants')
@login_required
@role_required('recruiter')
def all_applicants():
    if not current_user.company:
        flash('Please set up your company profile first.', 'info')
        return redirect(url_for('recruiter.setup_company'))
    
    applicants = JobService.get_applicants_for_company(current_user.company.id)
    return render_template('recruiter/all_applicants.html', applicants=applicants, company=current_user.company)

@recruiter_bp.route('/download_cv/<uuid:application_id>')
@login_required
@role_required('recruiter')
def download_cv(application_id):
    import os
    from flask import current_app, send_file, abort
    
    app_record = Application.query.get_or_404(application_id)
    
    # Ensure the job belongs to this recruiter's company
    if app_record.job.company_id != current_user.company.id:
        abort(403)
        
    # Fetch seeker's profile
    profile = app_record.user.profile
    if not profile or not profile.resume_path:
        flash('Candidate has not uploaded a resume.', 'error')
        return redirect(request.referrer or url_for('recruiter.dashboard'))
        
    # Resolve physical path
    file_path = os.path.join(current_app.root_path, 'static', profile.resume_path)
    
    if not os.path.exists(file_path):
        flash('Resume file not found on server.', 'error')
        return redirect(request.referrer or url_for('recruiter.dashboard'))
        
    mimetype = 'application/pdf'
    if file_path.endswith('.docx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"CV_{app_record.user.name.replace(' ', '_')}{os.path.splitext(file_path)[1]}"
    )
