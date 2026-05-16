from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.application import Application
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.services.job_service import JobService
from app.extensions import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_at.desc()).all()
    saved_jobs = JobService.get_saved_jobs(current_user.id)
    return render_template('user/dashboard.html', applications=applications, saved_jobs=saved_jobs)

@user_bp.route('/saved-jobs')
@login_required
def saved_jobs():
    jobs = JobService.get_saved_jobs(current_user.id)
    return render_template('user/saved_jobs.html', jobs=jobs)

import os
from werkzeug.utils import secure_filename
from flask import current_app
from app.models.user import Profile

@user_bp.route('/roadmap')
@login_required
def roadmap():
    # Placeholder for AI Roadmap (will be expanded in Part 4)
    return render_template('user/roadmap.html', roadmap=None)

@user_bp.route('/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('user.dashboard'))
        
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('user.dashboard'))
        
    if file:
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'resumes')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Ensure user has a profile
        if not current_user.profile:
            current_user.profile = Profile(user_id=current_user.id)
            db.session.add(current_user.profile)
            
        current_user.profile.resume_path = f"uploads/resumes/{filename}"
        
        # Ideally, we would parse the resume text here using pdfplumber/docx
        # For now, we'll just acknowledge the upload
        db.session.commit()
        
        flash('Resume uploaded successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    return redirect(url_for('user.dashboard'))

@user_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not current_user.profile:
        current_user.profile = Profile(user_id=current_user.id)
        db.session.add(current_user.profile)
        db.session.commit()
        
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.profile.headline = request.form.get('headline')
        current_user.profile.bio = request.form.get('bio')
        current_user.profile.location = request.form.get('location')
        current_user.profile.github_url = request.form.get('github_url')
        current_user.profile.linkedin_url = request.form.get('linkedin_url')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/edit_profile.html')
