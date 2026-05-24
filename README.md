# Be Your — AI-Powered Career Platform

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

> "Discover Yourself. Land Your Dream Job."

## 🔴 Live Demo / Development Tunnel
For development, you can expose the local application using Cloudflare tunnels:
```bash
npm run tunnel
```
This runs a local tunnel pointing to your active port, exposing the site via a dynamically generated Cloudflare URL. You should configure this generated URL as `SITE_URL` in your `.env` configuration file so that LinkedIn share links, verification emails, and other absolute URLs redirect correctly.

## What is Be Your?
Be Your is a next-generation AI-powered career platform designed to bridge the gap between human potential and industry expectations. It intelligently analyzes user profiles against market demands to generate personalized roadmaps, dynamic cover letters, and actionable feedback. By integrating advanced natural language processing with a sleek, distraction-free interface, it serves as the ultimate ecosystem for job seekers and recruiters alike.

## ✨ Key Features
**🧠 AI Intelligence**
- **Resume Scoring:** Instantly evaluate resumes against job requirements.
- **Skill Gap Analysis:** Identify exactly what skills you're missing for a role.
- **Job Matching:** Intelligent recommendation engine matching your profile.
- **Cover Letter:** Automatically generate highly-tailored cover letters.

**🚀 Career Growth**
- **Career Roadmap:** Step-by-step, 10-phase learning paths for specific roles.
- **Mock Interview:** AI-driven aptitude, behavioral, and technical interviews.
- **Code Playground:** Real-time problem solving with AI solution analysis.
- **Portfolio Analyzer:** Deep analysis of GitHub projects for credibility.

**🏢 Platform Features**
- **Recruiter Dashboard:** Seamlessly post, manage, and view job applications.
- **Admin Panel:** Complete system oversight, logs, and CSV reporting.
- **Badge System:** Earn exclusive badges by acing interviews and building portfolios.
- **Notifications:** Real-time alerts for application status updates.

**🔒 Security & Reliability**
- **Authentication:** Secure local auth + Google OAuth2 integration.
- **Rate Limiting:** Protection against spam and brute-force attacks.
- **CSP Headers:** Strict content security policies applied platform-wide.
- **Role-Based Access:** Isolated routes for Seekers, Recruiters, and Admins.

## 📸 Screenshots

| Landing Page | Seeker Dashboard |
|:---:|:---:|
| ![Landing](docs/screenshots/landing.png) | ![Dashboard](docs/screenshots/seeker-dashboard.png) |
| **AI Career Roadmap** | **Job Listings** |
| ![Roadmap](docs/screenshots/roadmap.png) | ![Jobs](docs/screenshots/jobs.png) |
| **Recruiter Dashboard** | **AI Mock Interview** |
| ![Recruiter](docs/screenshots/recruiter-dashboard.png) | ![Interview](docs/screenshots/interview.png) |
| **Portfolio Analyzer** | **Daily Sprint** |
| ![Portfolio](docs/screenshots/portfolio.png) | ![Sprint](docs/screenshots/sprint.png) |

## 🎯 How It Works

Be Your supports three distinct user journeys, each with its own 
tailored experience:

### 👨🎓 For Job Seekers (Students)
Sign up → Upload resume → Get AI-powered resume analysis → Generate 
a personalized career roadmap for your target role → Track daily 
learning progress with Daily Sprint streaks → Practice with AI mock 
interviews → Apply to jobs with auto-generated cover letters → 
Showcase your portfolio analyzed by AI.

### 🏢 For Recruiters
Sign up as recruiter → Post jobs with detailed requirements → View 
ranked applicants sorted by AI match score → Filter by skills, 
experience, and portfolio strength → Access deep analytics on 
applicant trends → Communicate with candidates through built-in 
notifications.

### 🛡️ For Admins
Oversee the entire platform with role-based dashboards → Manage 
users and recruiter accounts → Moderate job postings → View system 
logs and audit trails → Export CSV reports for analysis.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Client                     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────┐
│              Flask Application (Gunicorn)               │
├─────────────────────────────────────────────────────────┤
│  Routes Layer:                                          │
│  /auth  /user  /jobs  /recruiter  /admin  /ai  /sprint  │
├─────────────────────────────────────────────────────────┤
│  Services Layer:                                        │
│  AIService · MatchService · ResumeService               │
│  PortfolioService · SprintService · NotifyService       │
├─────────────────────────────────────────────────────────┤
│  Models Layer (SQLAlchemy ORM):                         │
│  User · Job · Application · Roadmap · Interview         │
│  Portfolio · Sprint · Notification                      │
└──────┬───────────────┬──────────────┬───────────────────┘
       │               │              │
       ▼               ▼              ▼
┌──────────┐    ┌─────────────┐  ┌─────────────────┐
│PostgreSQL│    │ Gemini AI   │  │ External APIs   │
│ Database │    │ (Roadmaps,  │  │ GitHub · SMTP   │
│          │    │  Interview) │  │ Google OAuth    │
└──────────┘    └─────────────┘  └─────────────────┘
```

**Key Design Decisions:**
- **Role-based access control** with `@role_required` decorator on every 
  protected route — seeker, recruiter, and admin routes are fully isolated
- **AI fallback strategy** — Gemini API for dynamic roadmaps with hardcoded 
  cache for popular roles to reduce cost
- **Async email** via Flask-Mail with threading
- **JSONB columns** for flexible storage of roadmap progress and AI outputs

## 🛠️ Tech Stack
| Category | Technology | Purpose |
|----------|------------|---------|
| **Backend** | Python 3.11, Flask | Core server + REST API |
| **Database** | PostgreSQL, SQLAlchemy | Relational data + ORM |
| **AI/ML** | scikit-learn, TF-IDF | Matching + scoring engine |
| **Auth** | Flask-Login, Authlib | Sessions + Google OAuth2 |
| **Frontend** | Tailwind CSS, Vanilla JS | Dark glassmorphism UI |
| **File Handling** | pdfplumber, python-docx| Resume text extraction |
| **DevOps** | Gunicorn, Render | WSGI + cloud deployment |
| **Testing** | pytest | 18+ automated tests |

## 📁 Project Structure
```text
be_your/
├── app/
│   ├── routes/     (9 blueprints: auth, user, jobs, recruiter, admin, ai, portfolio, resume, playground)
│   ├── models/     (11 SQLAlchemy models)
│   ├── services/   (8 service classes)
│   ├── utils/      (decorators, email, validators, resume_parser, notify)
│   └── templates/  (33 Jinja2 templates)
├── tests/          (conftest + 3 test files, 18 tests)
├── migrations/
├── requirements.txt
├── Procfile
└── README.md
```

## 🚀 Local Setup

**Step 1 — Clone:**
```bash
git clone https://github.com/yourusername/be-your.git
cd be-your
```

**Step 2 — Virtual environment (IMPORTANT: do NOT use Anaconda):**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**Step 3 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 4 — Environment setup:**
```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables section below)
```

**Step 5 — Database setup:**
```bash
# Make sure PostgreSQL is running locally
flask db upgrade
python seed.py           # Creates test data
python seed_jobs.py      # Seeds sample jobs
```

**Step 6 — Run:**
```bash
flask run
# Open http://localhost:5000
```

## ⚙️ Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key (random string) | Yes |
| `DATABASE_URL` | `postgresql://user:pass@localhost/be_your` | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth (console.cloud.google.com) | Optional |
| `GOOGLE_CLIENT_SECRET`| Google OAuth secret | Optional |
| `MAIL_USERNAME` | Gmail address for sending emails | Optional |
| `MAIL_PASSWORD` | Gmail App Password (not your real password)| Optional |
| `UPLOAD_FOLDER` | Path for resume uploads (`app/static/uploads/resumes`) | Yes |

## 🧪 Test Accounts (after running seed.py)
| Role | Email | Password |
|------|-------|----------|
| **Job Seeker** | seeker@example.com | Seeker@123 |
| **Recruiter** | recruiter@example.com | Recruiter@123 |
| **Admin** | Create manually (see below) | — |

**Create admin user manually:**
```python
flask shell
>>> from app.models.user import User; from app.extensions import db
>>> u = User(name="Admin", email="admin@beyour.com", role="admin")
>>> u.set_password("Admin@1234"); u.is_verified = True
>>> db.session.add(u); db.session.commit()
```

## 🔌 Key API Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Create account | No |
| POST | `/auth/login` | Login | No |
| GET | `/jobs/` | List all active jobs | No |
| POST | `/jobs/<id>/apply` | Apply to a job | Seeker |
| GET | `/ai/recommendations` | AI job recommendations | Seeker |
| GET | `/ai/interview/start` | Start mock interview | Seeker |
| POST | `/ai/cover-letter/generate`| Generate cover letter | Seeker |
| GET | `/portfolio/dashboard` | Portfolio analyzer | Seeker |
| GET | `/playground/playground` | Code challenges | Seeker |
| GET | `/admin/dashboard` | Admin overview | Admin |
| GET | `/admin/reports/export` | Download users CSV | Admin |

## 🧪 Running Tests
```bash
pytest tests/ -v
pytest tests/test_ai.py -v     # AI engine only
pytest tests/test_auth.py -v   # Auth only
```

## 🚢 Deploy to Render
1. Push to GitHub (make sure `.env` is in `.gitignore`)
2. Go to **render.com** → New Web Service
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn run:app` (already in `Procfile`)
6. Add Environment Variables in Render dashboard
7. Add PostgreSQL database in Render → copy `DATABASE_URL`
8. Deploy → wait ~2 mins → live!

## 📊 Platform Stats
- 11 database models · 9 Flask blueprints · 33 templates
- 12 AI methods · 18+ automated tests · 704-line AI engine

## 👤 Author
**Vishal Bhanopiya** | [LinkedIn](https://linkedin.com/in/vishalbhanopiya) | [GitHub](https://github.com/VishalBHANOPIYA)

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please make sure your code:
- Follows existing patterns (Flask blueprints, service layer)
- Includes tests for new features
- Passes existing tests: `pytest`
- Uses proper logging instead of print statements

## 📄 License
MIT — feel free to use, modify, and build on this project.
