from app.services.ai_service import AIService
from unittest.mock import MagicMock

def test_extract_skills_returns_list():
    result = AIService.extract_skills("Python Flask SQL")
    assert isinstance(result, list)

def test_extract_skills_finds_python():
    result = AIService.extract_skills("expert in Python and React")
    assert any("python" in r.lower() for r in result)

def test_extract_skills_empty_string():
    result = AIService.extract_skills("")
    assert result == []

def test_extract_skills_none():
    result = AIService.extract_skills(None)
    assert result == []

def test_calculate_match_score_similar_texts():
    text1 = "Python developer looking for backend role"
    text2 = "Python developer looking for backend role"
    score = AIService.calculate_match_score(text1, text2)
    assert score > 0.5

def test_calculate_match_score_empty():
    score = AIService.calculate_match_score("", "")
    assert score == 0.0

def test_analyze_resume_returns_score():
    result = AIService.analyze_resume("Python developer with Flask experience")
    assert 'score' in result
    assert isinstance(result['score'], (int, float))

def test_analyze_resume_empty_returns_zero():
    result = AIService.analyze_resume("")
    assert result['score'] == 0

def test_generate_roadmap_fullstack():
    result = AIService.generate_roadmap("Full Stack Developer", [])
    assert 'phases' in result

def test_generate_roadmap_has_projects():
    result = AIService.generate_roadmap("Frontend Developer", [])
    assert 'projects' in result

def test_generate_cover_letter_structure():
    mock_profile = MagicMock()
    mock_profile.user.name = "Test User"
    mock_profile.skills = ["Python"]
    
    mock_job = MagicMock()
    mock_job.title = "Backend Developer"
    mock_job.company.name = "TechCorp"
    mock_job.skills_required = ["Python", "Flask"]
    
    result = AIService.generate_cover_letter(mock_profile, mock_job)
    assert isinstance(result, str)
    assert "Dear Hiring Manager" in result or "Dear" in result

def test_generate_code_challenge():
    result = AIService.generate_code_challenge([])
    assert 'title' in result
    assert 'starter_code' in result or 'starter' in result
