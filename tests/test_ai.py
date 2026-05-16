import pytest
from app.services.ai_service import AIService

def test_extract_skills_python():
    text = "Experienced Python developer with Flask and SQL skills."
    skills = AIService.extract_skills(text)
    assert "Python" in skills
    assert "Flask" in skills
    assert "SQL" in skills

def test_extract_skills_empty():
    assert AIService.extract_skills("") == []

def test_calculate_match_nonzero():
    resume = "Python Flask Web Developer"
    job = "Looking for a Python developer with Flask experience"
    score = AIService.calculate_match_score(resume, job)
    assert score > 0

def test_calculate_match_empty():
    assert AIService.calculate_match_score("", "") == 0

def test_analyze_resume_empty():
    result = AIService.analyze_resume("")
    assert result['score'] == 0
    assert "No resume text found" in result['feedback'][0]
