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
    assert 'visual' in result
    assert 'data' in result
    assert 'steps' in result['data']

def test_generate_roadmap_has_projects():
    result = AIService.generate_roadmap("Frontend Developer", [])
    assert 'projects' in result['data']

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

def test_roadmap_schema_compliance():
    # Test Frontend Developer cached roadmap
    result = AIService.generate_roadmap("Frontend Developer", [])
    assert 'visual' in result
    assert 'data' in result
    data = result['data']
    assert 'steps' in data
    for step in data['steps']:
        assert 'sub_topics' in step
        for st in step['sub_topics']:
            assert 'id' in st
            assert 'completed' in st
            assert 'name' in st
            assert st['completed'] is False

def test_roadmap_toggle_milestone(client, db):
    # Register/login seeker user
    import uuid
    from app.models.user import User, Profile
    from app.models.roadmap import Roadmap
    
    email = f"seeker_{uuid.uuid4().hex[:8]}@example.com"
    user = User(name="Roadmap Tester", email=email, role="seeker")
    user.set_password("Password123!")
    db.session.add(user)
    db.session.flush()
    
    profile = Profile(user_id=user.id, skills=["Python"])
    db.session.add(profile)
    
    # Generate roadmap and save to db
    roadmap_data = AIService.generate_roadmap("Backend Developer", ["Python"])
    roadmap_record = Roadmap(
        user_id=user.id,
        target_role="Backend Developer",
        current_skills=["Python"],
        steps=roadmap_data['data'],
        visual_ascii=roadmap_data['visual']
    )
    db.session.add(roadmap_record)
    db.session.commit()
    
    # Authenticate client
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
        
    milestone_id = roadmap_data['data']['steps'][0]['sub_topics'][0]['id']
    
    # Send toggle request
    response = client.post('/ai/roadmap/toggle', json={
        'roadmap_id': str(roadmap_record.id),
        'milestone_id': milestone_id
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['completed'] is True
    assert data['progress_percentage'] > 0
    
    # Verify DB update
    updated_roadmap = Roadmap.query.get(roadmap_record.id)
    assert updated_roadmap.steps['steps'][0]['sub_topics'][0]['completed'] is True

