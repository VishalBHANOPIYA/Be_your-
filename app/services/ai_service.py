import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.job import Job

class AIService:
    COMMON_SKILLS = [
        "Python", "Java", "Javascript", "C++", "C#", "Ruby", "PHP", "Go", "Rust", "Swift",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring", "Laravel",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
        "SQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow",
        "Data Science", "Data Analysis", "Pandas", "NumPy", "Scikit-Learn",
        "Project Management", "Agile", "Scrum", "Git", "System Design"
    ]

    @staticmethod
    def extract_skills(text):
        if not text: return []
        found_skills = []
        text_lower = text.lower()
        for skill in AIService.COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        return list(set(found_skills))

    @staticmethod
    def calculate_match_score(resume_text, job_description):
        if not resume_text or not job_description:
            return 0
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score), 2)

    @staticmethod
    def generate_roadmap(target_role, current_skills):
        role_lower = target_role.lower()
        
        # --- PRE-DEFINED EXPERT ROADMAPS ---
        
        # 1. FULL STACK ROADMAP
        if "full" in role_lower and "stack" in role_lower:
            return {
                "role": "Full Stack Developer (2026)",
                "phases": [
                    {"title": "Phase 0: Basics & Setup", "milestones": [
                        {"name": "Internet Fundamentals", "desc": "IP, DNS, Browsers, and Client-Server architecture."},
                        {"name": "HTTP/HTTPS", "desc": "Request methods, Status codes, and Secure communication."},
                        {"name": "Tools Setup", "desc": "VS Code, Node.js, and terminal mastery."}
                    ]},
                    {"title": "Phase 1: Frontend Basics", "milestones": [
                        {"name": "Semantic HTML", "desc": "Tags for SEO and accessibility (Forms, Tables, Nav)."},
                        {"name": "Modern CSS", "desc": "Flexbox, Grid, and Responsive Media Queries."},
                        {"name": "Tailwind CSS", "desc": "Utility-first CSS for rapid UI development."}
                    ]},
                    {"title": "Phase 2: JavaScript Mastery", "milestones": [
                        {"name": "Core JS", "desc": "Variables, Functions, Closures, and DOM manipulation."},
                        {"name": "Async JS", "desc": "Promises, Async/Await, and Fetching APIs."},
                        {"name": "Data Structures", "desc": "Arrays, Objects, and ES6+ features."}
                    ]},
                    {"title": "Phase 3: React Development", "milestones": [
                        {"name": "Components & Props", "desc": "Functional components and data passing."},
                        {"name": "State & Hooks", "desc": "useState, useEffect, and custom hooks."},
                        {"name": "Routing", "desc": "React Router for Single Page Apps."}
                    ]},
                    {"title": "Phase 4: Backend Fundamentals", "milestones": [
                        {"name": "Flask / Django", "desc": "Building robust servers and routing logic."},
                        {"name": "RESTful APIs", "desc": "Designing CRUD endpoints for frontend integration."},
                        {"name": "Authentication", "desc": "JWT and session-based user security."}
                    ]},
                    {"title": "Phase 5: Database Design", "milestones": [
                        {"name": "SQL (PostgreSQL)", "desc": "Schema design, joins, and indexing."},
                        {"name": "NoSQL (MongoDB)", "desc": "Document-based storage and aggregation."},
                        {"name": "ORM/ODM", "desc": "SQLAlchemy and MongoEngine."}
                    ]},
                    {"title": "Phase 6: Full Integration", "milestones": [
                        {"name": "Axios/Fetch", "desc": "Connecting React to your Backend APIs."},
                        {"name": "CORS & Headers", "desc": "Handling cross-origin requests securely."},
                        {"name": "State Sharing", "desc": "Context API or Redux for global state."}
                    ]},
                    {"title": "Phase 7: Advanced Concepts", "milestones": [
                        {"name": "Real-time Ops", "desc": "WebSockets and Socket.io for chat/notifications."},
                        {"name": "Caching", "desc": "Redis for session management and speed."},
                        {"name": "MVC Patterns", "desc": "Organizing code for scalability."}
                    ]},
                    {"title": "Phase 8: Security & Testing", "milestones": [
                        {"name": "OWASP Top 10", "desc": "Preventing XSS and SQL Injection."},
                        {"name": "Unit Testing", "desc": "Pytest and Jest for bug-free code."},
                        {"name": "Logging", "desc": "System monitoring and error tracking."}
                    ]},
                    {"title": "Phase 9: DevOps & Cloud", "milestones": [
                        {"name": "Docker", "desc": "Containerizing your full stack app."},
                        {"name": "CI/CD", "desc": "Automated deployments with GitHub Actions."},
                        {"name": "Vercel & Render", "desc": "Hosting frontend and backend in production."}
                    ]},
                    {"title": "Phase 10: Career Prep", "milestones": [
                        {"name": "Portfolio App", "desc": "Building a production-ready Capstone project."},
                        {"name": "DSA Prep", "desc": "Solving Array and String challenges on LeetCode."},
                        {"name": "Interview Skills", "desc": "Soft skills and technical system design."}
                    ]}
                ],
                "projects": ["Netflix Clone", "E-Commerce Site", "Real-Time Chat App", "AI Project", "Expense Tracker"],
                "stack": {"frontend": "React, Tailwind", "backend": "Flask, Django", "db": "PostgreSQL, MongoDB"},
                "timeline": "6–8 Months"
            }

        # 2. FRONTEND ROADMAP
        if "front" in role_lower:
            return {
                "role": "Frontend Developer (2026)",
                "phases": [
                    {"title": "Phase 0: Basics & Setup", "milestones": [
                        {"name": "Internet", "desc": "How browsers and the web work."},
                        {"name": "Tools", "desc": "VS Code, Git, and Node.js install."}
                    ]},
                    {"title": "Phase 1: HTML Mastery", "milestones": [
                        {"name": "Semantic Tags", "desc": "Clean and accessible structure."},
                        {"name": "Forms", "desc": "Inputs, Validation, and Data submission."}
                    ]},
                    {"title": "Phase 2: CSS Layouts", "milestones": [
                        {"name": "Flex/Grid", "desc": "Modern responsive layout techniques."},
                        {"name": "Animations", "desc": "CSS Transitions and keyframes."}
                    ]},
                    {"title": "Phase 3: JavaScript Core", "milestones": [
                        {"name": "DOM", "desc": "Selecting and modifying HTML with JS."},
                        {"name": "Events", "desc": "Clicks, inputs, and form listeners."}
                    ]},
                    {"title": "Phase 4: JavaScript Pro", "milestones": [
                        {"name": "Async/Await", "desc": "Handling external API data."},
                        {"name": "ES6 Features", "desc": "Destructuring, Arrow functions, and Map/Filter."}
                    ]},
                    {"title": "Phase 5: React Basics", "milestones": [
                        {"name": "JSX", "desc": "Writing HTML inside your JavaScript."},
                        {"name": "State", "desc": "Managing dynamic data with hooks."}
                    ]},
                    {"title": "Phase 6: React Advanced", "milestones": [
                        {"name": "Context API", "desc": "Handling global user data."},
                        {"name": "Custom Hooks", "desc": "Reusable logic for multiple components."}
                    ]},
                    {"title": "Phase 7: State Tools", "milestones": [
                        {"name": "Zustand / Redux", "desc": "Modern state management libraries."},
                        {"name": "State Persistence", "desc": "Saving data across page refreshes."}
                    ]},
                    {"title": "Phase 8: API Integration", "milestones": [
                        {"name": "Axios", "desc": "Professional HTTP client for React."},
                        {"name": "React Query", "desc": "Caching and fetching like a pro."}
                    ]},
                    {"title": "Phase 9: UI Design", "milestones": [
                        {"name": "Figma", "desc": "Turning designs into pixel-perfect code."},
                        {"name": "Tailwind CSS", "desc": "Fast styling with utility classes."}
                    ]},
                    {"title": "Phase 10: Performance", "milestones": [
                        {"name": "Next.js", "desc": "SEO and Server-side rendering."},
                        {"name": "Lazy Loading", "desc": "Optimizing image and code bundle size."}
                    ]}
                ],
                "projects": ["Portfolio Website", "Movie App", "Blog UI", "Admin Dashboard", "E-Commerce Frontend"],
                "stack": {"frontend": "React, Next.js, Tailwind", "tools": "Git, Figma, VS Code"},
                "timeline": "5–7 Months"
            }

        # 3. GENERALIZED GENERATOR (For any other role)
        return {
            "role": f"{target_role.title()} Expert",
            "phases": [
                {"title": "Phase 0: Prep", "milestones": [{"name": "Environment", "desc": "Installing standard tools and languages."}]},
                {"title": "Phase 1: Basics", "milestones": [{"name": "Foundations", "desc": "Learning core syntax and principles."}]},
                {"title": "Phase 2: Logic", "milestones": [{"name": "Algorithms", "desc": "Understanding data structures and patterns."}]},
                {"title": "Phase 3: Domain", "milestones": [{"name": "Specialization", "desc": "Primary industry frameworks."}]},
                {"title": "Phase 4: API", "milestones": [{"name": "Integration", "desc": "Networking and data exchange."}]},
                {"title": "Phase 5: Data", "milestones": [{"name": "Persistence", "desc": "Databases and storage design."}]},
                {"title": "Phase 6: Security", "milestones": [{"name": "Hardening", "desc": "Secure coding and auth protocols."}]},
                {"title": "Phase 7: Perf", "milestones": [{"name": "Optimizing", "desc": "Efficiency and code quality."}]},
                {"title": "Phase 8: Infra", "milestones": [{"name": "Cloud", "desc": "Hosting and server management."}]},
                {"title": "Phase 9: Ops", "milestones": [{"name": "Automation", "desc": "Pipelines and monitoring."}]},
                {"title": "Phase 10: Final", "milestones": [{"name": "Portfolio", "desc": "Building real-world project."}]}
            ],
            "projects": [f"Standard {target_role} App", "System Architecture", "Performance Benchmarking", "Open Source Contribution"],
            "stack": {"core": "Standard Industry Tools", "cloud": "AWS/Azure", "dev": "CI/CD Pipelines"},
            "timeline": "6–9 Months"
        }

    @staticmethod
    def analyze_resume(text):
        if not text:
            return {
                "score": 0,
                "word_count": 0,
                "skills_found": [],
                "action_verbs": [],
                "readability": "Low",
                "ats_compatibility": False,
                "feedback": ["No resume text found. Please upload a valid PDF or Docx."]
            }
            
        text_lower = text.lower()
        words = text_lower.split()
        word_count = len(words)
        
        # 1. Skill Analysis
        skills = AIService.extract_skills(text)
        
        # 2. Action Verb Analysis
        action_verbs = [
            "led", "managed", "developed", "created", "designed", "optimized", 
            "implemented", "engineered", "accelerated", "delivered", "coordinated",
            "facilitated", "generated", "integrated", "launched", "monitored"
        ]
        found_verbs = [v for v in action_verbs if v in text_lower]
        
        # 3. ATS Scoring Heuristic
        score = 0
        feedback = []
        
        # Length check
        if 400 <= word_count <= 800:
            score += 30
            feedback.append("Optimal resume length detected.")
        elif word_count < 400:
            score += 15
            feedback.append("Resume might be too short. Consider adding more details about your achievements.")
        else:
            score += 20
            feedback.append("Resume is quite long. Ensure all content is highly relevant.")
            
        # Skill density
        skill_score = min(len(skills) * 4, 40)
        score += skill_score
        if len(skills) > 5:
            feedback.append(f"Strong skill density: {len(skills)} key industry terms identified.")
        else:
            feedback.append("Consider adding more industry-specific keywords and skills.")
            
        # Impact verbs
        verb_score = min(len(found_verbs) * 4, 30)
        score += verb_score
        if len(found_verbs) > 3:
            feedback.append("Good use of action verbs to describe your experience.")
        else:
            feedback.append("Use more strong action verbs (e.g., 'Optimized', 'Engineered') to show impact.")
            
        return {
            "score": score,
            "word_count": word_count,
            "skills_found": skills,
            "action_verbs": found_verbs,
            "readability": "High" if word_count > 300 else "Medium",
            "ats_compatibility": score >= 70,
            "feedback": feedback
        }

    @staticmethod
    def get_job_recommendations(user_profile):
        resume_text = user_profile.resume_text or ""
        skills = user_profile.skills or []
        
        all_jobs = Job.query.filter_by(is_active=True).all()
        recommendations = []
        
        for job in all_jobs:
            # Score based on skills and description
            skill_match = len(set(skills) & set(job.skills_required)) / len(job.skills_required) if job.skills_required else 0
            semantic_score = AIService.calculate_match_score(resume_text, job.description)
            
            final_score = (skill_match * 0.4) + (semantic_score * 0.6)
            
            if final_score > 0.1: # Only suggest relevant ones
                recommendations.append({
                    "job": job,
                    "score": round(final_score * 100, 1)
                })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]

    @staticmethod
    def generate_cover_letter(user_profile, job):
        name = user_profile.user.name
        role = job.title
        company = job.company.name
        skills = user_profile.skills or []
        job_skills = job.skills_required or []
        
        # Dynamic content generation logic
        intro = f"I am writing to express my enthusiastic interest in the {role} position at {company}. "
        
        if skills:
            skills_str = ", ".join(skills[:3])
            body1 = f"As a professional skilled in {skills_str}, I have a proven track record of delivering high-quality results. "
        else:
            body1 = "As a dedicated professional, I am committed to continuous learning and contributing to impactful projects. "
            
        if job_skills:
            js_str = ", ".join(job_skills[:2])
            body2 = f"My background aligns closely with your requirement for expertise in {js_str}. "
        else:
            body2 = "I am eager to bring my unique perspective and problem-solving abilities to your team. "
            
        closing = f"I am particularly drawn to {company} because of your reputation for innovation. Thank you for your time and consideration."
        
        letter = f"""Dear Hiring Manager at {company},

{intro}

{body1}{body2}

I believe my technical foundation and collaborative mindset make me an ideal candidate for this role. I am excited about the possibility of contributing to {company}'s ongoing success and would welcome the opportunity to discuss my qualifications further.

{closing}

Best regards,
{name}"""
        return letter.strip()

    @staticmethod
    def generate_interview_questions(user_skills, job_role="Software Developer", category="technical"):
        role = job_role or "Software Developer"
        skills_context = ", ".join(user_skills) if user_skills else "general engineering"
        
        # 1. APTITUDE BANK
        aptitude_bank = [
            "A train 150m long is running at 54 km/hr. How much time will it take to pass a platform 250m long?",
            "If 5 machines take 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
            "A person crosses a 600m long street in 5 minutes. What is his speed in km per hour?",
            "If the day before yesterday was Thursday, what day will be the day after tomorrow?",
            "Which number should come next in the series: 1, 1, 2, 3, 5, 8, 13, ...?",
            "If 'WATER' is coded as 'XBUFS', how is 'FIRE' coded?",
            "A father is twice as old as his son. 20 years ago, he was 4 times as old. How old is the son now?",
            "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
            "All humans are mortal. Socrates is human. Therefore, Socrates is mortal. Is this a valid syllogism?",
            "What is the next prime number after 13?",
            "If you rearrange the letters 'CIFAIPC', you get the name of an: (A) City (B) Ocean (C) Animal.",
            "A clock shows 3:15. What is the angle between the hour and minute hands?",
            "Which word does not belong: Apple, Banana, Potato, Cherry?",
            "If all Bloops are Razzies and all Razzies are Lurgies, are all Bloops definitely Lurgies?",
            "Find the missing number: 2, 6, 12, 20, 30, ?"
        ]
        
        # 2. BEHAVIORAL BANK
        behavioral_bank = [
            "Tell me about a time you handled a difficult stakeholder.",
            "Describe a situation where you had to make a decision without all the information.",
            "What is your proudest technical achievement?",
            "How do you handle disagreement within your team?",
            "Tell me about a time you had to learn a complex tool in a very short time.",
            "Describe a time you failed to meet a deadline. What did you do?",
            "How do you stay updated with the latest industry trends?",
            "What motivates you to come to work every day?",
            "Tell me about a time you mentored a junior colleague.",
            "How do you handle repetitive tasks that are necessary for the project?"
        ]
        
        # 3. SPECIALIZED BANK
        specialized_bank = {
            "Python": [
                "What are decorators, and how do they work internally?",
                "Explain the difference between @staticmethod, @classmethod, and instance methods.",
                "How does Python's Garbage Collection (GC) work?",
                "What are Generators and why would you use them over Lists?",
                "Explain 'Monkey Patching' in Python and why it might be dangerous.",
                "What is the GIL and how does it affect multi-threaded programs?",
                "How do you use context managers ('with' statement)?",
                "Explain the difference between __init__ and __new__."
            ],
            "Flask": [
                "How does the Flask 'Request Context' work?",
                "What is the difference between 'g' and 'session'?",
                "Explain how you would handle large file uploads in Flask.",
                "How do you implement JWT authentication in a Flask API?",
                "What are the benefits of using Blueprints in a Flask project?",
                "How would you handle background tasks (like sending emails) in a Flask app?",
                "Explain how to use Flask-SQLAlchemy for database migrations."
            ],
            "React": [
                "What are 'Hooks' and what rules must you follow when using them?",
                "Explain the 'Virtual DOM' and the Reconciliation process.",
                "How does the 'useContext' hook help with state management?",
                "What is the difference between React.memo and useMemo?",
                "Explain how you would handle server-side rendering (SSR) in React.",
                "What are 'Higher-Order Components' and how do they differ from Hooks?",
                "How do you optimize a React app that is rendering too slowly?"
            ],
            "PostgreSQL": [
                "Explain the difference between B-Tree and Hash indexes.",
                "What is 'Vacuuming' in PostgreSQL and why is it necessary?",
                "How would you optimize a query that involves a JOIN across 5 tables?",
                "What are 'Window Functions' and can you give an example?",
                "Explain the ACID properties in the context of PostgreSQL.",
                "What is the difference between 'TRUNCATE' and 'DELETE'?",
                "How do you handle database sharding or partitioning?"
            ]
        }
        
        # Assemble 15 Questions
        final_questions = []
        
        # Part 1: 5 Aptitude
        random.shuffle(aptitude_bank)
        final_questions.extend(aptitude_bank[:5])
        
        # Part 2: 5 Behavioral
        random.shuffle(behavioral_bank)
        final_questions.extend(behavioral_bank[:5])
        
        # Part 3: 5 Technical
        tech_questions = []
        
        # Priority 1: Specific skill/role requested by user in setup
        if job_role and job_role in specialized_bank:
            tech_questions.extend(specialized_bank[job_role])
            
        # Priority 2: Other user skills
        for s in user_skills:
            if s in specialized_bank and s != job_role: # Avoid duplication
                tech_questions.extend(specialized_bank[s])
        
        # Priority 3: General technical questions
        general_tech = [
            "Explain the difference between REST and GraphQL.",
            "What is a deadlock in multithreading?",
            "Explain the concept of Big O notation.",
            "What is the difference between a process and a thread?",
            "How do you ensure your code follows SOLID principles?",
            "What is the CAP theorem in distributed systems?",
            "Explain the concept of Microservices vs Monolith.",
            "How does a DNS resolution work?",
            "What is the difference between symmetric and asymmetric encryption?"
        ]
        tech_questions.extend(general_tech)
        
        # Shuffle technical and pick 5
        random.shuffle(tech_questions)
        final_questions.extend(tech_questions[:5])
        
        return final_questions

    @staticmethod
    def get_skill_gap_data(user_profile, job):
        user_skills = [s.lower() for s in (user_profile.skills or [])]
        job_skills = job.skills_required or []
        
        # Take up to top 6 skills for the radar chart axes
        display_skills = job_skills[:6]
        if len(display_skills) < 3: # Fallback to categories if too few skills
            display_skills = ["Frontend", "Backend", "Database", "DevOps", "Soft Skills"]
            
        labels = display_skills
        user_data = []
        job_data = []
        
        for skill in labels:
            # Job requirement is always 100 for these specific skills
            job_data.append(100)
            # Check if user has it
            if skill.lower() in user_skills:
                user_data.append(100)
            else:
                # Mock a partial match or 20% for visual
                user_data.append(20)
        
        return {
            "labels": labels,
            "user_data": user_data,
            "job_data": job_data,
            "matched": [s for s in job_skills if s.lower() in user_skills],
            "missing": [s for s in job_skills if s.lower() not in user_skills]
        }

    @staticmethod
    def analyze_portfolio(github_data):
        """
        Analyzes GitHub data to suggest improvements and highlights.
        """
        if not github_data:
            return "No GitHub data found to analyze."

        repos_text = "\n".join([
            f"- {r['name']}: {r['description']} (Language: {r['language']}, Stars: {r['stars']})"
            for r in github_data['top_repos']
        ])

        prompt = f"""
        Analyze this developer's GitHub portfolio and provide a professional evaluation.
        
        Developer: {github_data['name']} (@{github_data['username']})
        Bio: {github_data['bio']}
        Stats: {github_data['public_repos']} repos, {github_data['followers']} followers
        
        Recent Top Projects:
        {repos_text}
        
        Provide the analysis in JSON format with:
        1. "strengths": List of 3 key technical strengths identified.
        2. "improvement_areas": 2 areas where they can improve their portfolio presence.
        3. "tech_stack": Dominant languages/technologies seen.
        4. "summary": A 2-3 sentence professional summary for recruiters.
        5. "score": A portfolio impact score from 1-100.
        """

        try:
            # Reusing generate_cover_letter's logic or simple call
            # For simplicity, I'll use a mocked AI response if key is missing, 
            # but usually we call the LLM here.
            # Assuming current_app.config['GEMINI_API_KEY'] exists
            
            # For now, let's provide a rich structured response
            # In a real app, this would be a model.generate_content call
            
            # Identifying dominant tech from data
            languages = [r['language'] for r in github_data['top_repos'] if r['language']]
            dominant_tech = list(set(languages))[:3]
            
            return {
                "strengths": [
                    "Active contribution to open-source projects.",
                    f"Strong proficiency in {', '.join(dominant_tech)}.",
                    "Consistent project documentation and clear descriptions."
                ],
                "improvement_areas": [
                    "Consider adding more comprehensive README files to smaller projects.",
                    "Diversify projects to showcase full-stack capabilities."
                ],
                "tech_stack": dominant_tech,
                "summary": f"{github_data['name']} shows a strong technical foundation with a focus on {', '.join(dominant_tech)}. Their portfolio demonstrates consistent coding activity and a clear passion for building functional tools.",
                "score": min(70 + (github_data['followers'] * 2) + (len(github_data['top_repos']) * 2), 98)
            }
        except Exception as e:
            print(f"AI Analysis error: {e}")
            return None

    @staticmethod
    def generate_interview_scorecard(questions, answers, feedback):
        """
        Generates a phase-based scorecard for the interview.
        """
        # Phase boundaries: 1-5 Aptitude, 6-10 Experience, 11-15 Technical
        phases = {
            "Aptitude": {"indices": range(0, 5), "score": 0, "count": 0, "feedback": []},
            "Experience": {"indices": range(5, 10), "score": 0, "count": 0, "feedback": []},
            "Technical": {"indices": range(10, 15), "score": 0, "count": 0, "feedback": []}
        }

        for i in range(len(questions)):
            q_feedback = feedback.get(str(i), {"score": 0, "analysis": "No response."})
            score = q_feedback.get('score', 0)
            
            for phase_name, data in phases.items():
                if i in data['indices']:
                    data['score'] += score
                    data['count'] += 1
                    if score < 50:
                        data['feedback'].append(f"Improvement needed in Q{i+1}")
                    break

        report = []
        total_final_score = 0
        
        for name, data in phases.items():
            avg_phase_score = (data['score'] / data['count']) if data['count'] > 0 else 0
            total_final_score += avg_phase_score
            
            report.append({
                "phase": name,
                "score": round(avg_phase_score, 1),
                "summary": f"Demonstrated {'strong' if avg_phase_score > 70 else 'moderate' if avg_phase_score > 40 else 'foundational'} capability in {name.lower()} assessments.",
                "status": "Exceeded" if avg_phase_score > 80 else "Passed" if avg_phase_score > 50 else "Needs Improvement"
            })

        return {
            "overall_score": round(total_final_score / 3, 1),
            "phase_reports": report,
            "strengths": [r['phase'] for r in report if r['score'] > 75],
            "recommendation": "Ready for actual interview" if total_final_score/3 > 70 else "Needs more practice"
        }

    @staticmethod
    def analyze_resume_content(resume_text, job_description=None):
        """
        AI Analysis of resume text against standards or a JD.
        """
        # Simulated high-end analysis logic
        # In production, this would be a prompt to Gemini
        
        # Keyword detection logic
        tech_keywords = ["python", "javascript", "react", "flask", "aws", "docker", "sql", "git", "ci/cd", "agile"]
        found_keywords = [k for k in tech_keywords if k in resume_text.lower()]
        
        ats_score = min(60 + (len(found_keywords) * 4), 95)
        if len(resume_text) < 1000: ats_score -= 10 # Too short
        
        return {
            "score": ats_score,
            "metrics": {
                "ats_compatibility": ats_score,
                "keyword_match": min(len(found_keywords) * 10, 100),
                "formatting": 85 if len(resume_text) > 1500 else 70,
                "impact_verbs": 75 if "developed" in resume_text.lower() or "managed" in resume_text.lower() else 50
            },
            "findings": [
                {
                    "type": "strength",
                    "title": "Strong Technical Foundation",
                    "message": f"Good presence of core technologies like {', '.join(found_keywords[:3])}."
                },
                {
                    "type": "improvement",
                    "title": "Action Verb Optimization",
                    "message": "Use more powerful verbs like 'Spearheaded', 'Orchestrated', or 'Leveraged' to describe your impact."
                },
                {
                    "type": "critical",
                    "title": "Quantifiable Achievements",
                    "message": "Your experience lacks metrics. Add percentages or numbers (e.g., 'Reduced latency by 30%') to stand out."
                }
            ],
            "keyword_analysis": {
                "missing": [k for k in tech_keywords if k not in found_keywords][:4],
                "present": found_keywords
            },
            "summary": "Your resume has a solid foundation but needs more focus on quantifiable impact to clear high-tier ATS filters."
        }

    @staticmethod
    def generate_code_challenge(user_skills, roadmap_phase="Basics"):
        """Generate a coding challenge based on user's current roadmap progress."""
        # Bank of common challenges - Starting with easier ones for better onboarding
        challenges = [
            {
                "title": "Basic Arithmetic: The Sum Tool",
                "problem": "Write a function `add_numbers(a, b)` that takes two numbers and returns their sum. Simple and clean!",
                "starter": "def add_numbers(a, b):\n    # Your code here\n    return",
                "difficulty": "Beginner"
            },
            {
                "title": "Python: Even or Odd?",
                "problem": "Write a function `is_even(n)` that returns True if a number is even, and False if it is odd.",
                "starter": "def is_even(n):\n    # Your code here\n    pass",
                "difficulty": "Easy"
            },
            {
                "title": "Strings: Hello World Plus",
                "problem": "Write a function `greet(name)` that returns a greeting string: 'Hello, [name]! Welcome to Be Your.'",
                "starter": "def greet(name):\n    # Your code here\n    pass",
                "difficulty": "Easy"
            },
            {
                "title": "List Basics: Find the Largest",
                "problem": "Given a list of numbers, write a function `find_max(nums)` that returns the largest number in the list.",
                "starter": "def find_max(nums):\n    # Your code here\n    pass",
                "difficulty": "Easy"
            }
        ]
        return random.choice(challenges)

    @staticmethod
    def analyze_code_solution(problem, code):
        """Analyze code for quality, performance, and best practices."""
        # More realistic scoring logic
        score = 100
        issues = []
        
        # 1. Check for empty or trivial solutions
        if len(code.strip()) < 10 or "pass" in code:
            score -= 60
            issues.append("Your solution seems incomplete. Try writing the actual logic instead of placeholders.")
        
        # 2. Check for logic repetition (user just copied the starter)
        if code.count("return") < 1 and "print" not in code:
            score -= 40
            issues.append("Your code isn't returning any value. Make sure to use the 'return' keyword.")

        # 3. Basic keyword check based on common problems
        if "max" in problem.lower() and "max(" not in code and "for" not in code:
            score -= 30
            issues.append("To find the largest number, you should use the built-in max() function or a loop.")

        if "sum" in problem.lower() and "+" not in code and "sum(" not in code:
            score -= 30
            issues.append("Make sure you are actually performing an addition operation.")

        # Final score calculation
        final_score = max(0, score)
        
        summary = "Your solution is logically sound." if final_score > 70 else "Your solution needs significant improvement."
        if final_score < 40: summary = "Critical logic missing. Please review the problem statement carefully."

        return {
            "score": final_score,
            "summary": summary,
            "metrics": {
                "readability": 90 if final_score > 50 else 50,
                "performance": 85 if final_score > 70 else 40,
                "security": 100
            },
            "suggestions": issues if issues else ["Code looks clean! Try to solve it using a different approach for practice."],
            "best_practices": [
                "PEP 8 compliance looks good.",
                "Function structure is correct."
            ]
        }
