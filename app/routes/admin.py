from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.utils.decorators import role_required
from app.extensions import db

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
        "recruiters": User.query.filter_by(role='recruiter').count(),
        "recent_users": User.query.order_by(User.created_at.desc()).limit(10).all(),
        "recent_jobs": Job.query.order_by(Job.created_at.desc()).limit(10).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/user/<uuid:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own admin account.", "danger")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"User {user.name} status updated.", "success")
    return redirect(url_for('admin.users'))

@admin_bp.route('/jobs')
@login_required
@role_required('admin')
def jobs():
    jobs_list = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=jobs_list)

@admin_bp.route('/job/<uuid:job_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job listing removed by admin.", "info")
    return redirect(url_for('admin.jobs'))
