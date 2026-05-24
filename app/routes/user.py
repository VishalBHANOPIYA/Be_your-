from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.application import Application
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.models.user import Profile
from app.services.job_service import JobService
from app.services.ai_service import AIService
from app.utils.resume_parser import ResumeParser
from app.extensions import db, limiter
import os
import uuid as uuid_module
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
@role_required('seeker')
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_at.desc()).all()
    saved_jobs = JobService.get_saved_jobs(current_user.id)
    
    # Calculate average match score
    avg_match = 0
    if applications:
        total_score = sum([app.resume_score for app in applications if app.resume_score])
        avg_match = int(total_score / len(applications))
        
    # Calculate profile progress
    fields = ['name']
    prof_fields = ['headline', 'bio', 'location', 'github_url', 'linkedin_url', 'resume_path']
    filled = 1 if current_user.name else 0
    total = 1 + len(prof_fields)
    
    if current_user.profile:
        for f in prof_fields:
            if getattr(current_user.profile, f):
                filled += 1
                
    profile_progress = int((filled / total) * 100)
    
    return render_template('user/dashboard.html', applications=applications, saved_jobs=saved_jobs, profile_progress=profile_progress, avg_match=avg_match)

@user_bp.route('/saved-jobs')
@login_required
@role_required('seeker')
def saved_jobs():
    jobs = JobService.get_saved_jobs(current_user.id)
    return render_template('user/saved_jobs.html', jobs=jobs)

@user_bp.route('/roadmap')
@login_required
@role_required('seeker')
def roadmap():
    from app.models.roadmap import Roadmap
    roadmap_record = Roadmap.query.filter_by(user_id=current_user.id).first()
    if roadmap_record:
        return render_template('user/roadmap.html', roadmap=roadmap_record.steps, target_role=roadmap_record.target_role, roadmap_id=roadmap_record.id)
    return render_template('user/roadmap.html', roadmap=None)


@user_bp.route('/upload-resume', methods=['POST'])
@login_required
@role_required('seeker')
@limiter.limit("10 per day", methods=["POST"])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('user.dashboard'))
        
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('user.dashboard'))
        
    if file:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.pdf', '.docx']:
            flash("Only PDF and DOCX files are allowed.", "danger")
            return redirect(url_for('user.dashboard'))
            
        secure_name = f"resume_{current_user.id}_{uuid_module.uuid4().hex}{ext}"
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'resumes')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, secure_name)
        file.save(file_path)
        
        # --- RESUME INTELLIGENCE ---
        raw_text = ResumeParser.extract_text(file_path)
        clean_text = ResumeParser.clean_text(raw_text)
        extracted_skills = AIService.extract_skills(clean_text)
        
        # Ensure user has a profile
        if not current_user.profile:
            current_user.profile = Profile(user_id=current_user.id)
            db.session.add(current_user.profile)
            
        current_user.profile.resume_path = f"uploads/resumes/{secure_name}"
        current_user.profile.resume_text = clean_text
        
        if not current_user.profile.skills:
            current_user.profile.skills = extracted_skills
            
        analysis = AIService.analyze_resume(clean_text)
        current_user.profile.resume_score = analysis['score']
            
        db.session.commit()
        
        flash('Resume uploaded successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    return redirect(url_for('user.dashboard'))

@user_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
@role_required('seeker')
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
        
        skills_raw = request.form.get('skills', '')
        if skills_raw:
            current_user.profile.skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
            
        exp_raw = request.form.get('experience', '')
        if exp_raw:
            current_user.profile.experience = [{"details": exp_raw.strip()}]
            
        edu_raw = request.form.get('education', '')
        if edu_raw:
            current_user.profile.education = [{"details": edu_raw.strip()}]
        
        # Handle Avatar Upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    secure_avatar_name = f"avatar_{current_user.id}_{uuid_module.uuid4().hex}{ext}"
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, secure_avatar_name)
                    file.save(file_path)
                    current_user.avatar_url = f"uploads/avatars/{secure_avatar_name}"
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/edit_profile.html')

@user_bp.route('/resume-analysis')
@login_required
@role_required('seeker')
def resume_analysis():
    if not current_user.profile or not current_user.profile.resume_text:
        flash('Please upload your resume first to see the analysis.', 'info')
        return redirect(url_for('user.dashboard'))
        
    analysis = AIService.analyze_resume(current_user.profile.resume_text)
    return render_template('user/resume_analysis.html', analysis=analysis)

@user_bp.route('/notifications')
@login_required
@role_required('seeker')
def get_notifications():
    from app.models.notification import Notification
    from flask import jsonify
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    
    # Mark as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if hasattr(n.created_at, 'isoformat') else n.created_at
    } for n in notifs])

@user_bp.route('/notifications/count')
@login_required
@role_required('seeker')
def get_notifications_count():
    from app.models.notification import Notification
    from flask import jsonify
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})
