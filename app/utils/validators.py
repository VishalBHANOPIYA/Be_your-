import re

def validate_email(email: str) -> (bool, str):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, email):
        return True, ""
    return False, "Invalid email format."

def validate_password(password: str) -> (bool, str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."
    if not any(char in "!@#$%^&*()_+-=" for char in password):
        return False, "Password must contain a special character (!@#$%^&*()_+-=)."
    return True, ""

def validate_name(name: str) -> (bool, str):
    if not (2 <= len(name) <= 120):
        return False, "Name must be between 2 and 120 characters."
    regex = r'^[a-zA-Z\s\-]+$'
    if re.match(regex, name):
        return True, ""
    return False, "Name must be 2–120 letters only."

def sanitize_text(text: str, max_length: int = 5000) -> str:
    if not text:
        return ""
    return text.strip().replace('\x00', '')[:max_length]

def validate_url(url: str) -> bool:
    if not url:
        return True
    return url.startswith(('http://', 'https://'))
