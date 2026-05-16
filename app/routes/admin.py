from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.company import Company
from app.models.admin_log import AdminLog
from app.models.interview import Interview
from app.utils.decorators import role_required
from app.extensions import db
import io
import csv
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = {
        "total_users": User.query.count(),
        "total_jobs": Job.query.count(),
        "total_applications": Application.query.count(),
        "seekers": User.query.filter_by(role='seeker').count(),
        "total_recruiters": User.query.filter_by(role='recruiter').count(),
        "total_interviews": Interview.query.filter_by(status='completed').count(),
        "recent_users": User.query.order_by(User.created_at.desc()).limit(10).all(),
        "recent_jobs": Job.query.order_by(Job.created_at.desc()).limit(10).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    users_query = User.query.order_by(User.created_at.desc())
    if q:
        users_query = users_query.filter(
            (User.name.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%'))
        )
    
    users_pagination = users_query.paginate(page=page, per_page=20)
    return render_template('admin/users.html', users_pagination=users_pagination, q=q)

@admin_bp.route('/user/<uuid:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own admin account.", "danger")
    else:
        user.is_active = not user.is_active
        
        # Log action
        log = AdminLog(
            admin_id=current_user.id,
            action=f"{'Activated' if user.is_active else 'Deactivated'} user",
            target_type="user",
            target_id=user.id
        )
        db.session.add(log)
        db.session.commit()
        flash(f"User {user.name} status updated.", "success")
    return redirect(url_for('admin.users'))

@admin_bp.route('/recruiters')
@login_required
@role_required('admin')
def recruiters():
    page = request.args.get('page', 1, type=int)
    # Join with Company to see verification status
    recruiters_query = db.session.query(User, Company).filter(User.role == 'recruiter').outerjoin(Company, Company.recruiter_id == User.id)
    recruiters_pagination = recruiters_query.paginate(page=page, per_page=20)
    return render_template('admin/recruiters.html', recruiters_pagination=recruiters_pagination)

@admin_bp.route('/recruiters/<uuid:user_id>/verify', methods=['POST'])
@login_required
@role_required('admin')
def verify_recruiter(user_id):
    company = Company.query.filter_by(recruiter_id=user_id).first()
    if not company:
        flash("This recruiter has no company profile yet.", "warning")
        return redirect(url_for('admin.recruiters'))
    
    company.is_verified = not company.is_verified
    
    # Log action
    log = AdminLog(
        admin_id=current_user.id,
        action="Verified company" if company.is_verified else "Unverified company",
        target_type="company",
        target_id=company.id
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Company {company.name} verification status updated.", "success")
    return redirect(url_for('admin.recruiters'))

@admin_bp.route('/jobs')
@login_required
@role_required('admin')
def jobs():
    page = request.args.get('page', 1, type=int)
    jobs_pagination = Job.query.order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/jobs.html', jobs_pagination=jobs_pagination)

@admin_bp.route('/job/<uuid:job_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Log action
    log = AdminLog(
        admin_id=current_user.id,
        action="Deleted job listing",
        target_type="job",
        target_id=job.id
    )
    db.session.add(log)
    db.session.delete(job)
    db.session.commit()
    flash("Job listing removed by admin.", "info")
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/logs')
@login_required
@role_required('admin')
def logs():
    page = request.args.get('page', 1, type=int)
    logs_pagination = AdminLog.query.order_by(AdminLog.timestamp.desc()).paginate(page=page, per_page=30)
    return render_template('admin/logs.html', logs_pagination=logs_pagination)

@admin_bp.route('/reports/export')
@login_required
@role_required('admin')
def export_users():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Role', 'Active', 'Verified', 'Joined Date'])
    
    users = User.query.all()
    for u in users:
        writer.writerow([u.id, u.name, u.email, u.role, u.is_active, u.is_verified, u.created_at])
        
    filename = f"be_your_users_{datetime.now().strftime('%Y-%m-%d')}.csv"
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    return response
