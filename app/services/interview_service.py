import random
from app.models.interview import Interview
from app.extensions import db

class InterviewService:
    QUESTION_BANK = {
        "technical": [
            "What is the difference between a list and a tuple in Python?",
            "Explain the concept of decorators in Python.",
            "How does memory management work in Python?",
            "What is the purpose of the 'self' keyword in Python classes?",
            "Explain the difference between deep copy and shallow copy.",
            "What are Python's built-in data types?",
            "How do you handle exceptions in Python?",
            "What is the difference between @staticmethod and @classmethod?",
            "Explain the GIL (Global Interpreter Lock) in Python.",
            "What is a generator and how does it differ from a list?"
        ],
        "behavioral": [
            "Tell me about a time you faced a difficult challenge and how you overcame it.",
            "Why do you want to join our company?",
            "How do you handle conflict in a team setting?",
            "Describe a situation where you had to learn a new technology quickly.",
            "What are your greatest strengths and weaknesses?",
            "Tell me about a time you failed and what you learned.",
            "How do you prioritize your work when you have multiple deadlines?",
            "Describe a time you had to work with a difficult coworker.",
            "Where do you see yourself in five years?",
            "How do you handle stress and pressure?"
        ],
        "system_design": [
            "How would you design a URL shortener like Bitly?",
            "Explain the concept of Load Balancing.",
            "How would you design a scalable notification system?",
            "What is Sharding in database management?",
            "How would you design a Rate Limiter?"
        ],
        "hr": [
            "Tell me about yourself.",
            "What are your salary expectations?",
            "Why should we hire you over other candidates?",
            "Tell me about your most significant professional achievement.",
            "How would your current manager describe you?"
        ]
    }

    @staticmethod
    def start_session(user_id, job_role=None, category="technical"):
        from app.models.user import User
        from app.services.ai_service import AIService
        
        user = User.query.get(user_id)
        user_skills = user.profile.skills if user and user.profile else []
        
        # Use AI to generate specialized questions based on user skills
        selected_questions = AIService.generate_interview_questions(user_skills, job_role, category)
        
        interview = Interview(
            user_id=user_id,
            job_role=job_role,
            category=category,
            questions=selected_questions,
            answers={},
            feedback={},
            status="started"
        )
        db.session.add(interview)
        db.session.commit()
        return interview

    @staticmethod
    def submit_answer(interview_id, question_index, answer_text):
        interview = Interview.query.get(interview_id)
        if not interview:
            return None, "Interview session not found"
            
        answers = dict(interview.answers) if interview.answers else {}
        answers[str(question_index)] = answer_text
        interview.answers = answers
        
        # Simulated AI Feedback Logic
        feedback = dict(interview.feedback) if interview.feedback else {}
        
        # Simple analysis based on length and keywords
        score = 0
        if len(answer_text) > 100: score += 40
        elif len(answer_text) > 50: score += 20
        
        keywords = ["example", "result", "team", "learned", "achieved", "python", "flask", "design"]
        for word in keywords:
            if word in answer_text.lower():
                score += 5
        
        score = min(score, 100)
        
        if score > 70:
            msg = "Excellent answer! You provided good depth and context."
        elif score > 40:
            msg = "Good effort. Try to provide more specific examples to strengthen your point."
        else:
            msg = "This answer was a bit brief. Consider using the STAR method (Situation, Task, Action, Result)."
            
        feedback[str(question_index)] = {
            "score": score,
            "analysis": msg
        }
        interview.feedback = feedback
        
        db.session.commit()
        return interview, None

    @staticmethod
    def finish_session(interview_id):
        interview = Interview.query.get(interview_id)
        if interview:
            interview.status = "completed"
            
            from app.services.ai_service import AIService
            scorecard = AIService.generate_interview_scorecard(
                interview.questions, 
                interview.answers, 
                interview.feedback
            )
            
            # Merge scorecard into feedback
            full_feedback = dict(interview.feedback) if interview.feedback else {}
            full_feedback['scorecard'] = scorecard
            interview.feedback = full_feedback
            interview.total_score = scorecard['overall_score']
            
            db.session.commit()

            # --- BADGE AWARDING LOGIC ---
            if scorecard['overall_score'] >= 80:
                from app.services.badge_service import BadgeService
                from app.models.user import User
                user = User.query.get(interview.user_id)
                if user:
                    BadgeService.check_and_award_interview_badge(user, scorecard['overall_score'], interview.job_role or "Technical")
            
        return interview
