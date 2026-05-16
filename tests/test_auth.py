import pytest
from app.models.user import User

def test_register_page_loads(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b"Create your account" in response.data

def test_register_success(client, db):
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'Password123!',
        'role': 'seeker'
    }, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.name == 'Test User'

def test_register_duplicate_email(client, db):
    # First registration
    res1 = client.post('/auth/register', data={
        'name': 'User Alpha',
        'email': 'dup@example.com',
        'password': 'Password123!',
        'role': 'seeker'
    }, follow_redirects=True)
    
    # Verify first registration worked
    user = User.query.filter_by(email='dup@example.com').first()
    assert user is not None, f"First registration failed. Check validators or DB."
    
    # Duplicate registration
    response = client.post('/auth/register', data={
        'name': 'User Beta',
        'email': 'dup@example.com',
        'password': 'Password123!',
        'role': 'seeker'
    }, follow_redirects=True)
    assert b"Email already registered" in response.data

def test_register_invalid_email(client):
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'notanemail',
        'password': 'Password123!',
        'role': 'seeker'
    }, follow_redirects=True)
    assert b"Invalid email format" in response.data

def test_register_weak_password(client):
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'weak@example.com',
        'password': 'abc',
        'role': 'seeker'
    }, follow_redirects=True)
    assert b"Password must be at least 8 characters" in response.data

def test_login_page_loads(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_login_wrong_password(client, db):
    client.post('/auth/register', data={
        'name': 'Login User',
        'email': 'login@example.com',
        'password': 'Password123!',
        'role': 'seeker'
    })
    response = client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'WrongPassword'
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data

def test_logout_requires_login(client):
    response = client.get('/auth/logout')
    # Should redirect to login page
    assert response.status_code == 302
    assert '/auth/login' in response.location
