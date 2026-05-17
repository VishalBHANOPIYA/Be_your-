from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.github_service import GitHubService
from app.services.ai_service import AIService
from app.services.portfolio_service import PortfolioService
from app.models.user import User, Profile
from app.extensions import db

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    if not current_user.profile or not current_user.profile.github_url:
        return jsonify({
            "success": False, 
            "error": "Please add your GitHub URL to your profile first."
        }), 400
    
    github_url = current_user.profile.github_url
    github_data = GitHubService.get_user_data(github_url)
    
    if not github_data:
        return jsonify({
            "success": False, 
            "error": "Could not fetch data from GitHub. Please check your URL."
        }), 404
        
    analysis = AIService.analyze_portfolio(github_data)
    
    if not analysis:
        return jsonify({
            "success": False, 
            "error": "AI Analysis failed. Please try again later."
        }), 500
        
    return jsonify({
        "success": True,
        "github_data": github_data,
        "analysis": analysis
    })

@portfolio_bp.route('/dashboard')
@login_required
def portfolio_dashboard():
    return render_template('user/portfolio_analysis.html')

# --- NEW PORTFOLIO BUILDER FEATURES ---

@portfolio_bp.route('/builder', methods=['GET', 'POST'])
@login_required
def builder():
    # Ensure profile exists
    if not current_user.profile:
        current_user.profile = Profile(user_id=current_user.id)
        db.session.add(current_user.profile)
        db.session.commit()
        
    profile = current_user.profile
    
    if request.method == 'POST':
        profile.headline = request.form.get('headline')
        profile.bio = request.form.get('bio')
        profile.location = request.form.get('location')
        profile.portfolio_theme = request.form.get('theme', 'zinc_indigo')
        profile.visibility = request.form.get('visibility') == 'public'
        
        # Parse Social Links
        socials = {
            "github": request.form.get('social_github', ''),
            "linkedin": request.form.get('social_linkedin', ''),
            "twitter": request.form.get('social_twitter', ''),
            "website": request.form.get('social_website', '')
        }
        profile.portfolio_socials = socials
        
        # Parse Showcase Projects (Supports dynamic inputs)
        project_titles = request.form.getlist('project_title[]')
        project_descs = request.form.getlist('project_desc[]')
        project_techs = request.form.getlist('project_tech[]')
        project_urls = request.form.getlist('project_url[]')
        
        projects_data = []
        for i in range(len(project_titles)):
            if project_titles[i].strip():
                projects_data.append({
                    "title": project_titles[i].strip(),
                    "desc": project_descs[i].strip() if i < len(project_descs) else "",
                    "tech": project_techs[i].strip() if i < len(project_techs) else "",
                    "url": project_urls[i].strip() if i < len(project_urls) else ""
                })
        profile.portfolio_projects = projects_data
        
        db.session.commit()
        flash('Public Web Resume / Portfolio settings saved successfully!', 'success')
        return redirect(url_for('portfolio.builder'))
        
    # Standard values fallbacks
    socials = profile.portfolio_socials or {"github": "", "linkedin": "", "twitter": "", "website": ""}
    projects = profile.portfolio_projects or []
    
    # URL Slug representation for the current user using unique 4-character UUID suffix
    id_suffix = str(current_user.id).replace('-', '')[:4]
    username_slug = current_user.name.lower().replace(" ", "-") + "-" + id_suffix
    public_url = url_for('portfolio.public_portfolio', username_slug=username_slug, _external=True)
    
    return render_template(
        'user/portfolio_builder.html', 
        profile=profile, 
        socials=socials, 
        projects=projects,
        public_url=public_url
    )

@portfolio_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    if not current_user.profile or not current_user.profile.resume_text:
        return jsonify({
            "success": False,
            "message": "Please upload a verified resume first to serve as the builder template!"
        }), 400
        
    success = PortfolioService.generate_from_resume(current_user.profile)
    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Website portfolio successfully generated! Refreshing visual workspace."
        })
        
    return jsonify({
        "success": False,
        "message": "AI analysis mapping failed. Try uploading your resume again."
    }), 500

@portfolio_bp.route('/public/<username_slug>', methods=['GET'])
def public_portfolio(username_slug):
    # Lookup logic matching slugs, IDs, or emails robustly
    user = None
    
    # 1. New lookup: extract suffix from slug, find user by UUID prefix
    # Slug format: "name-parts-xxxx" where xxxx is first 4 chars of UUID (no dashes)
    # Split on last '-' to get suffix
    parts = username_slug.rsplit('-', 1)
    if len(parts) == 2:
        id_suffix = parts[1]  # e.g. "a3f2"
        # Find all users whose UUID (no dashes) starts with id_suffix
        users = User.query.all()
        user = next((u for u in users if str(u.id).replace('-', '').startswith(id_suffix)), None)
        
    if not user:
        # Fallback: try name match
        search_name = username_slug.replace('-', ' ')
        user = User.query.filter(User.name.ilike(f'%{search_name}%')).first()
        
    # 2. Try raw UUID query
    if not user:
        try:
            user = User.query.get(username_slug)
        except Exception:
            pass
            
    # 3. Try exact email match
    if not user:
        user = User.query.filter_by(email=username_slug).first()
        
    # Check bounds
    if not user or not user.profile:
        return render_template('errors/404.html'), 404
        
    profile = user.profile
    
    # Check visibility gate
    if not profile.visibility:
        return render_template('portfolio/private_profile.html', user=user), 403
        
    socials = profile.portfolio_socials or {"github": "", "linkedin": "", "twitter": "", "website": ""}
    projects = profile.portfolio_projects or []
    
    return render_template(
        'portfolio/public_portfolio.html',
        user=user,
        profile=profile,
        socials=socials,
        projects=projects,
        theme=profile.portfolio_theme or 'zinc_indigo'
    )
