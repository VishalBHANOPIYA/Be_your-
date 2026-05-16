# Be Your — AI-Powered Career Platform

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)
![MIT License](https://img.shields.io/badge/License-MIT-green)

## Live Demo
[be-your.onrender.com](https://be-your.onrender.com)

## What is Be Your?
Be Your is a comprehensive career intelligence platform designed to bridge the gap between job seekers and their dream roles. By leveraging AI-driven resume analysis, ATS scoring, and personalized career roadmaps, it empowers users to optimize their professional profiles and master the hiring process.

## Key Features
✅ **AI Resume Intelligence**: Real-time ATS scoring and skill gap analysis.  
✅ **Career Architect**: 10-phase personalized learning roadmaps for any role.  
✅ **Job Match Engine**: Semantic matching (TF-IDF) between resumes and listings.  
✅ **Mock Interviews**: Practice sessions with AI-generated feedback.  
✅ **Recruiter Suite**: Powerful tools for candidate ranking and verification.  
✅ **Admin Analytics**: Full platform oversight with CSV export capabilities.  
✅ **Secure Auth**: Google OAuth2 integration and password reset workflows.  
✅ **Role-Based Access**: Specialized dashboards for Seekers, Recruiters, and Admins.  
✅ **Security Hardened**: Rate limiting, CSP, and secure file handling built-in.

## Tech Stack
| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.11, Flask | Core server and API logic |
| **Database** | PostgreSQL | Scalable relational data storage |
| **AI/ML** | scikit-learn, TF-IDF | Recommendation and matching engine |
| **Auth** | Flask-Login, Authlib | Session management and OAuth2 |
| **Frontend** | Tailwind CSS, Vanilla JS | Premium dark glassmorphism UI |
| **Testing** | Pytest | Comprehensive unit and integration testing |
| **Deployment** | Render, Gunicorn | High-performance production hosting |

## Architecture
```text
Browser → Flask Blueprints → Services Layer → [PostgreSQL] + [AI Engine]
```

## Project Structure
```text
be_your/
├── app/
│   ├── routes/     (auth, user, jobs, recruiter, admin, ai)
│   ├── models/     (SQLAlchemy schemas)
│   ├── services/   (AI, Job, Auth business logic)
│   ├── utils/      (Validators, Email, Resume Parser)
│   ├── templates/  (25+ Jinja2 Templates)
│   └── static/     (CSS, JS, Uploads)
├── tests/          (Pytest suites)
├── migrations/     (DB Versioning)
├── requirements.txt
└── Procfile
```

## Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/be_your.git
   cd be_your
   ```
2. **Setup environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your values (PostgreSQL, Secret Keys, etc.).
4. **Initialize Database**:
   ```bash
   flask db upgrade
   python seed.py
   ```
5. **Run the application**:
   ```bash
   flask run
   ```

## Environment Variables
| Variable | Description | Required |
| :--- | :--- | :--- |
| `SECRET_KEY` | Flask session secret | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Optional |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Optional |
| `MAIL_USERNAME` | SMTP server email | Optional |
| `MAIL_PASSWORD` | SMTP app password | Optional |

## Running Tests
Execute the full test suite using Pytest:
```bash
pytest tests/ -v
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
[Your Name] — [LinkedIn](https://linkedin.com/in/yourprofile) — [GitHub](https://github.com/yourusername)
