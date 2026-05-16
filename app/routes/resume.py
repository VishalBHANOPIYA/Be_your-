from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.services.resume_service import ResumeService
import os
import uuid
from werkzeug.utils import secure_filename

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/resume/optimize', methods=['GET', 'POST'])
@login_required
def optimize():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'error')
            return redirect(request.url)
            
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Ensure upload folder exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Extract text and analyze
            resume_text = ResumeService.extract_text(file_path)
            if not resume_text:
                flash('Could not extract text from your resume. Please try a different format.', 'error')
                return redirect(request.url)
                
            jd = request.form.get('job_description')
            analysis = ResumeService.analyze_resume(resume_text, jd)
            
            # In a real app, we might store this in DB. For now, we'll pass it to template
            # or store it in session if it's small.
            return render_template('user/resume_results.html', analysis=analysis)
            
    return render_template('user/resume_optimizer.html')
