from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.github_service import GitHubService
from app.services.ai_service import AIService
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
