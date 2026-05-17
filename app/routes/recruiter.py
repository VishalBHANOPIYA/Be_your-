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

@recruiter_bp.route('/analytics')
@login_required
@role_required('recruiter')
def analytics():
    if not current_user.company:
        flash('Please set up your company profile first.', 'info')
        return redirect(url_for('recruiter.setup_company'))
    
    # 1. Fetch all jobs belonging to the recruiter's company
    jobs = Job.query.filter_by(company_id=current_user.company.id).all()
    job_ids = [j.id for j in jobs]
    
    # 2. Get total applications count across all their jobs
    total_apps = 0
    shortlisted_hired = 0
    job_app_counts = []
    job_titles = []
    
    if job_ids:
        # Get count per job
        apps = Application.query.filter(Application.job_id.in_(job_ids)).all()
        total_apps = len(apps)
        
        # Calculate conversion metrics
        shortlisted_hired = sum(1 for a in apps if a.status in ['shortlisted', 'hired'])
        
        for job in jobs:
            count = sum(1 for a in apps if a.job_id == job.id)
            job_app_counts.append(count)
            job_titles.append(job.title)
            
    # 3. Calculate conversion rate: (shortlisted + hired) / total applications * 100
    conversion_rate = 0.0
    if total_apps > 0:
        conversion_rate = round((shortlisted_hired / total_apps) * 100, 1)
        
    return render_template(
        'recruiter/analytics.html',
        company=current_user.company,
        total_jobs=len(jobs),
        total_applications=total_apps,
        conversion_rate=conversion_rate,
        job_titles=job_titles,
        job_app_counts=job_app_counts
    )

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
