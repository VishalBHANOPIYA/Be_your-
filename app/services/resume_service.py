import os
import pdfplumber
import docx
from app.services.ai_service import AIService
from flask import current_app

class ResumeService:
    @staticmethod
    def extract_text(file_path):
        """Extract text from PDF or DOCX files."""
        extension = os.path.splitext(file_path)[1].lower()
        text = ""
        
        try:
            if extension == '.pdf':
                from app.utils.resume_parser import ResumeParser
                text = ResumeParser.extract_text_from_pdf(file_path)
            elif extension == '.docx':
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                # Treat as plain text
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
            
        return text.strip()

    @staticmethod
    def analyze_resume(resume_text, job_description=None):
        """Analyze resume and provide optimization feedback."""
        # Use AI Service for deep analysis
        analysis = AIService.analyze_resume_content(resume_text, job_description)
        
        # --- BADGE AWARDING LOGIC ---
        from flask_login import current_user
        if current_user.is_authenticated and analysis.get('score', 0) >= 90:
            from app.services.badge_service import BadgeService
            BadgeService.check_and_award_portfolio_badge(current_user, analysis['score'])
            
        return analysis
