import pytest
from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application
import uuid

@pytest.fixture
def recruiter_user(db):
    """Fixture to generate a clean testing recruiter user."""
    email = f"recruiter_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Recruiter Jane",
        email=email,
        role="recruiter",
        is_verified=True
    )
    user.set_password("Password123!")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def seeker_user(db):
    """Fixture to generate a clean testing seeker user."""
    email = f"seeker_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Seeker Bob",
        email=email,
        role="seeker",
        is_verified=True
    )
    user.set_password("Password123!")
    db.session.add(user)
    db.session.commit()
    return user

def test_analytics_unauthenticated(client):
    """Ensure unauthenticated users are restricted from recruiter analytics."""
    response = client.get('/recruiter/analytics')
    # Should redirect to login page or get 302
    assert response.status_code == 302

def test_analytics_restricted_role_seeker(client, seeker_user):
    """Ensure seekers are forbidden from accessing recruiter analytics."""
    # Login seeker
    client.post('/auth/login', data={
        'email': seeker_user.email,
        'password': 'Password123!'
    })
    
    response = client.get('/recruiter/analytics')
    # role_required returns 403 Forbidden for incorrect role
    assert response.status_code == 403

def test_analytics_recruiter_no_company(client, recruiter_user):
    """Ensure recruiters without companies are redirected to company setup."""
    # Login recruiter
    client.post('/auth/login', data={
        'email': recruiter_user.email,
        'password': 'Password123!'
    })
    
    response = client.get('/recruiter/analytics')
    # Redirects to /recruiter/setup-company
    assert response.status_code == 302
    assert '/recruiter/setup-company' in response.location

def test_analytics_recruiter_success(client, db, recruiter_user, seeker_user):
    """Ensure recruiter with company can access analytics and load aggregations."""
    # 1. Setup company
    company = Company(
        recruiter_id=recruiter_user.id,
        name="Test Corp",
        website="https://test.com",
        description="A great test company",
        location="San Francisco"
    )
    db.session.add(company)
    db.session.commit()
    
    # 2. Add some jobs and applications to verify aggregation logic runs fine
    job = Job(
        company_id=company.id,
        title="Software Engineer",
        description="Write code.",
        skills_required=["Python"],
        location="Remote",
        salary_min=100000,
        salary_max=120000,
        is_active=True
    )
    db.session.add(job)
    db.session.commit()
    
    app = Application(
        job_id=job.id,
        user_id=seeker_user.id,
        resume_score=85.0,
        status="applied",
        cover_note="Experienced python developer"
    )
    db.session.add(app)
    db.session.commit()
    
    # Login recruiter
    client.post('/auth/login', data={
        'email': recruiter_user.email,
        'password': 'Password123!'
    })
    
    response = client.get('/recruiter/analytics')
    assert response.status_code == 200
    
    # Verify expected structure and elements in response
    assert b"Recruiter Analytics" in response.data
    assert b"Software Engineer" in response.data
    assert b"Application Status" in response.data
    assert b"Top 5 Applicants" in response.data
    assert b"Seeker Bob" in response.data
