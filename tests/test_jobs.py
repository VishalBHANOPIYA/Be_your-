import pytest
from app.models.job import Job
from app.models.user import User
from app.models.company import Company
import uuid

@pytest.fixture
def sample_job(db):
    # Use a unique email for every test run
    email = f"rec_{uuid.uuid4().hex[:8]}@example.com"
    user = User(name="Recruiter", email=email, role="recruiter")
    user.set_password("Password123!")
    db.session.add(user)
    db.session.flush()
    
    company = Company(name="Test Corp", recruiter_id=user.id)
    db.session.add(company)
    db.session.flush()
    
    job = Job(
        title="Python Developer",
        description="Write some Python code.",
        company_id=company.id,
        skills_required=["Python", "Flask"],
        salary_min=80000,
        salary_max=120000,
        location="Remote",
        is_active=True
    )
    db.session.add(job)
    db.session.commit()
    return job

def test_jobs_list_loads(client):
    response = client.get('/jobs/')
    assert response.status_code == 200

def test_job_search(client, sample_job):
    response = client.get('/jobs/?q=Python')
    assert response.status_code == 200
    assert b"Python Developer" in response.data

def test_jobs_pagination(client):
    response = client.get('/jobs/?page=1')
    assert response.status_code == 200

def test_apply_requires_login(client, sample_job):
    response = client.post(f'/jobs/{sample_job.id}/apply')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_save_requires_login(client, sample_job):
    response = client.post(f'/jobs/{sample_job.id}/save')
    assert response.status_code == 302
    assert '/auth/login' in response.location
