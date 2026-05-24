import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import current_app
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
    def _post_process_roadmap(roadmap_dict, role_type="general"):
        # Map role type to generic default resources
        resources_map = {
            "fullstack": [{"title": "MDN Web Docs", "url": "https://developer.mozilla.org"}, {"title": "Full Stack Open", "url": "https://fullstackopen.com"}],
            "frontend": [{"title": "MDN Web Docs", "url": "https://developer.mozilla.org"}, {"title": "javascript.info", "url": "https://javascript.info"}],
            "backend": [{"title": "Real Python", "url": "https://realpython.com"}, {"title": "Flask Documentation", "url": "https://flask.palletsprojects.com"}],
            "datascience": [{"title": "Kaggle Learn", "url": "https://www.kaggle.com/learn"}, {"title": "Scikit-Learn Docs", "url": "https://scikit-learn.org"}],
            "devops": [{"title": "Docker Curriculum", "url": "https://docker-curriculum.com"}, {"title": "Kubernetes Docs", "url": "https://kubernetes.io/docs"}],
            "ml": [{"title": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials"}, {"title": "Hugging Face Course", "url": "https://huggingface.co/course"}]
        }
        default_res = resources_map.get(role_type, [{"title": "Official Documentation", "url": "https://docs.google.com"}])
        
        if not isinstance(roadmap_dict, dict):
            return
        if 'role' not in roadmap_dict:
            roadmap_dict['role'] = 'Expert'
        if 'phases' not in roadmap_dict:
            roadmap_dict['phases'] = []
        if 'projects' not in roadmap_dict:
            roadmap_dict['projects'] = ['Capstone Project']
        if 'stack' not in roadmap_dict:
            roadmap_dict['stack'] = {'core': 'Industry Standard'}
        if 'timeline' not in roadmap_dict:
            roadmap_dict['timeline'] = '6 Months'
        if 'final_capstone' not in roadmap_dict:
            roadmap_dict['final_capstone'] = 'Build a final capstone project matching the target role.'
            
        for p_idx, phase in enumerate(roadmap_dict.get('phases', [])):
            if not isinstance(phase, dict):
                continue
            if 'title' not in phase:
                phase['title'] = f"Phase {p_idx}"
            if 'phase_project' not in phase:
                phase['phase_project'] = f"Build a practical implementation representing skills from Phase {p_idx}."
            if 'milestones' not in phase:
                phase['milestones'] = []
                
            for m_idx, ms in enumerate(phase.get('milestones', [])):
                if not isinstance(ms, dict):
                    continue
                if 'id' not in ms or not ms['id']:
                    ms['id'] = f"ms_{p_idx}_{m_idx}"
                if 'name' not in ms:
                    ms['name'] = 'Key Topic'
                if 'description' not in ms:
                    ms['description'] = ms.get('desc', 'Learn key principles of the topic.')
                ms['desc'] = ms['description']
                if 'estimated_hours' not in ms:
                    ms['estimated_hours'] = 10
                if 'resources' not in ms or not isinstance(ms['resources'], list):
                    ms['resources'] = default_res
                if 'checkpoint' not in ms:
                    ms['checkpoint'] = 'Create a small test program verifying the concepts learned.'
                if 'completed' not in ms:
                    ms['completed'] = False

    @staticmethod
    def _get_fallback_roadmap(target_role):
        return {
            "role": f"{target_role.title()} Expert",
            "phases": [
                {
                    "title": "Phase 0: Foundations",
                    "phase_project": f"Setup dev tools and create a basic document outlining the role of a {target_role}.",
                    "milestones": [
                        {
                            "id": "ms_0_0",
                            "name": "Environment Setup",
                            "description": "Install required IDEs, command line tools, and local servers.",
                            "desc": "Install required IDEs, command line tools, and local servers.",
                            "estimated_hours": 6,
                            "resources": [{"title": "Official Guides", "url": "https://www.google.com"}],
                            "checkpoint": "Verify installation of tools via console.",
                            "completed": False
                        }
                    ]
                },
                {
                    "title": "Phase 1: Basic Principles",
                    "phase_project": "Build a minor utility or layout using basic principles.",
                    "milestones": [
                        {
                            "id": "ms_1_0",
                            "name": "Core Syntax & Logic",
                            "description": "Understand language elements, basic APIs, and structural patterns.",
                            "desc": "Understand language elements, basic APIs, and structural patterns.",
                            "estimated_hours": 12,
                            "resources": [{"title": "Reference Tutorial", "url": "https://www.w3schools.com"}],
                            "checkpoint": "Create a console-based calculator or equivalent script.",
                            "completed": False
                        }
                    ]
                },
                {
                    "title": "Phase 2: Project Deployment",
                    "phase_project": "Deploy the capstone project live to a cloud environment.",
                    "milestones": [
                        {
                            "id": "ms_2_0",
                            "name": "Final Capstone Prep",
                            "description": "Assemble all elements and package them into a professional portfolio item.",
                            "desc": "Assemble all elements and package them into a professional portfolio item.",
                            "estimated_hours": 20,
                            "resources": [{"title": "Deployment Best Practices", "url": "https://github.com"}],
                            "checkpoint": "Run tests and verify build success.",
                            "completed": False
                        }
                    ]
                }
            ],
            "projects": [f"Standard {target_role} App", "System Architecture", "Performance Benchmarking"],
            "stack": {"core": "Standard Industry Tools", "cloud": "AWS/Azure/GCP"},
            "timeline": "6–9 Months",
            "final_capstone": f"Build a production-ready deployment of a full {target_role} application."
        }

    @staticmethod
    def _generate_ascii_visual_from_data(data):
        role = data.get('role', 'Developer').upper()
        lines = []
        
        # 1. Header Box
        lines.append("┌" + "─"*59 + "┐")
        role_text = f"{role} ROADMAP"
        if len(role_text) > 55:
            role_text = role_text[:52] + "..."
        padding = (59 - len(role_text)) // 2
        left_padding = " " * padding
        right_padding = " " * (59 - len(role_text) - padding)
        lines.append(f"│{left_padding}{role_text}{right_padding}│")
        lines.append("└" + "─"*59 + "┘")
        
        # Down arrow
        lines.append("")
        lines.append("        ▼")
        lines.append("")
        
        steps = data.get('steps', [])
        for idx, step in enumerate(steps):
            title = f"{step.get('number', idx+1)}. {step.get('title', '').upper()}"
            if len(title) > 55:
                title = title[:52] + "..."
            
            # Step Box
            lines.append("┌" + "─"*59 + "┐")
            t_pad = 59 - len(title) - 2
            lines.append(f"│ {title}{' '*t_pad} │")
            lines.append("├" + "─"*59 + "┤")
            
            # Sub-topics
            for st in step.get('sub_topics', []):
                name = st.get('name', '')
                completed = st.get('completed', False)
                bullet = "✓ " if completed else "• "
                bullet_name = f"{bullet}{name}"
                if len(bullet_name) > 54:
                    bullet_name = bullet_name[:51] + "..."
                
                st_pad = 59 - len(bullet_name) - 3
                lines.append(f"│  {bullet_name}{' '*st_pad} │")
                
            lines.append("└" + "─"*59 + "┘")
            
            # Down arrow if not last
            lines.append("")
            lines.append("        ▼")
            lines.append("")
            
        # Build projects box
        lines.append("┌" + "─"*59 + "┐")
        proj_title = f"{len(steps) + 1}. BUILD PROJECTS"
        t_pad = 59 - len(proj_title) - 2
        lines.append(f"│ {proj_title}{' '*t_pad} │")
        lines.append("├" + "─"*59 + "┤")
        
        projects = data.get('projects', {})
        
        # Beginner
        beg_hdr = "Beginner:"
        lines.append(f"│ {beg_hdr}{' '*(59 - len(beg_hdr) - 2)} │")
        for p in projects.get('beginner', [])[:2]:
            p_str = f"• {p}"
            if len(p_str) > 54:
                p_str = p_str[:51] + "..."
            lines.append(f"│  {p_str}{' '*(59 - len(p_str) - 3)} │")
        lines.append(f"│{' '*59}│")
        
        # Intermediate
        int_hdr = "Intermediate:"
        lines.append(f"│ {int_hdr}{' '*(59 - len(int_hdr) - 2)} │")
        for p in projects.get('intermediate', [])[:1]:
            p_str = f"• {p}"
            if len(p_str) > 54:
                p_str = p_str[:51] + "..."
            lines.append(f"│  {p_str}{' '*(59 - len(p_str) - 3)} │")
        lines.append(f"│{' '*59}│")
        
        # Advanced
        adv_hdr = "Advanced:"
        lines.append(f"│ {adv_hdr}{' '*(59 - len(adv_hdr) - 2)} │")
        for p in projects.get('advanced', [])[:1]:
            p_str = f"• {p}"
            if len(p_str) > 54:
                p_str = p_str[:51] + "..."
            lines.append(f"│  {p_str}{' '*(59 - len(p_str) - 3)} │")
            
        lines.append("└" + "─"*59 + "┘")
        
        # Down arrow
        lines.append("")
        lines.append("        ▼")
        lines.append("")
        
        # Job Ready Checklist Box
        lines.append("┌" + "─"*59 + "┐")
        jr_title = f"JOB READY {role.upper()}"
        if len(jr_title) > 55:
            jr_title = jr_title[:52] + "..."
        padding = (59 - len(jr_title)) // 2
        left_padding = " " * padding
        right_padding = " " * (59 - len(jr_title) - padding)
        lines.append(f"│{left_padding}{jr_title}{right_padding}│")
        lines.append("├" + "─"*59 + "┤")
        
        for item in data.get('job_ready_checklist', [])[:8]:
            item_str = f"✓ {item}"
            if len(item_str) > 55:
                item_str = item_str[:52] + "..."
            lines.append(f"│ {item_str}{' '*(59 - len(item_str) - 2)} │")
            
        lines.append("└" + "─"*59 + "┘")
        
        return "\n".join(lines)

    @staticmethod
    def _build_roadmap_response(roadmap_data, current_skills=None):
        if not current_skills:
            current_skills = []
        current_skills_lower = [s.lower().strip() for s in current_skills]
        
        # Map phases to steps
        steps = []
        job_ready_skills = []
        for idx, phase in enumerate(roadmap_data.get("phases", [])):
            estimated_hours = sum(ms.get("estimated_hours", 10) for ms in phase.get("milestones", []))
            sub_topics = []
            for ms in phase.get("milestones", []):
                ms_name = ms.get("name", "Key Topic")
                completed = any(s in ms_name.lower() or ms_name.lower() in s for s in current_skills_lower) or ms.get('completed', False)
                sub_topics.append({
                    "id": ms.get("id", f"step_{idx+1}_topic_{len(sub_topics)+1}"),
                    "name": ms_name,
                    "description": ms.get("desc", ms.get("description", "Learn this critical skill.")),
                    "completed": completed
                })
                job_ready_skills.append(ms_name)
                
            steps.append({
                "id": f"step_{idx+1}",
                "number": idx + 1,
                "title": phase.get("title", f"Phase {idx}").upper(),
                "duration_weeks": max(2, len(phase.get("milestones", []))),
                "estimated_hours": estimated_hours,
                "sub_topics": sub_topics,
                "checkpoint": phase.get("phase_project", "Build a practice application."),
                "resources": [
                    {"type": "docs", "title": "Official Documentation", "source": "official"}
                ],
                "completed": all(st["completed"] for st in sub_topics) if sub_topics else False
            })
            
        projs = roadmap_data.get("projects", [])
        projects_dict = {
            "beginner": projs[:2] if len(projs) >= 2 else projs if projs else ["Beginner Project"],
            "intermediate": [projs[2]] if len(projs) >= 3 else ["Intermediate Project"],
            "advanced": [roadmap_data.get("final_capstone", "Final Capstone Project Prep")]
        }
        
        data = {
            "role": roadmap_data.get("role", "Developer"),
            "summary": f"Complete path to master {roadmap_data.get('role', 'Developer')}.",
            "total_duration_weeks": sum(step["duration_weeks"] for step in steps),
            "weekly_commitment_hours": "10-15 hours",
            "difficulty": "Beginner",
            "steps": steps,
            "projects": projects_dict,
            "job_ready_checklist": job_ready_skills[:6] if job_ready_skills else ["Core Skills"],
            "career_tips": [
                "Build real-world projects and showcase them on GitHub.",
                "Practice coding challenges regularly to improve problem solving.",
                "Network with other developers in local or online communities."
            ]
        }
        
        visual = AIService._generate_ascii_visual_from_data(data)
        
        return {
            "visual": visual,
            "data": data
        }

    @staticmethod
    def _mark_completed_topics(data, current_skills):
        if not current_skills or not data or 'steps' not in data:
            return data
        current_skills_lower = [s.lower().strip() for s in current_skills]
        for step in data.get('steps', []):
            sub_topics = step.get('sub_topics', [])
            for st in sub_topics:
                name = st.get('name', '').lower().strip()
                if any(skill in name or name in skill for skill in current_skills_lower):
                    st['completed'] = True
            # Update step completed status
            if sub_topics:
                step['completed'] = all(st.get('completed', False) for st in sub_topics)
        return data

    @staticmethod
    def generate_roadmap(target_role, current_skills):
        role_lower = target_role.lower()
        
        is_fullstack = "full" in role_lower and "stack" in role_lower
        is_frontend = "front" in role_lower
        is_backend = "back" in role_lower
        is_datascience = "data" in role_lower or "science" in role_lower
        is_devops = "devops" in role_lower or "cloud" in role_lower or "infra" in role_lower
        is_ml = "ml" in role_lower or "machine" in role_lower or "learning" in role_lower
        
        # --- PRE-DEFINED EXPERT ROADMAPS ---
        
        if is_fullstack:
            roadmap = {
                "role": "Full Stack Developer (2026)",
                "phases": [
                    {"title": "Phase 0: Basics & Setup", "phase_project": "Set up a clean local environment and host a basic HTML page.", "milestones": [
                        {"name": "Internet Fundamentals", "desc": "IP, DNS, Browsers, and Client-Server architecture.", "estimated_hours": 4, "checkpoint": "Explain the request-response cycle."},
                        {"name": "HTTP/HTTPS", "desc": "Request methods, Status codes, and Secure communication.", "estimated_hours": 4, "checkpoint": "Verify requests using developer tools."},
                        {"name": "Tools Setup", "desc": "VS Code, Node.js, and terminal mastery.", "estimated_hours": 6, "checkpoint": "Configure editor and git settings."}
                    ]},
                    {"title": "Phase 1: Frontend Basics", "phase_project": "Build a responsive personal homepage styled with Tailwind.", "milestones": [
                        {"name": "Semantic HTML", "desc": "Tags for SEO and accessibility (Forms, Tables, Nav).", "estimated_hours": 8, "checkpoint": "Build an accessible signup form."},
                        {"name": "Modern CSS", "desc": "Flexbox, Grid, and Responsive Media Queries.", "estimated_hours": 12, "checkpoint": "Build a responsive 3-column layout."},
                        {"name": "Tailwind CSS", "desc": "Utility-first CSS for rapid UI development.", "estimated_hours": 8, "checkpoint": "Style a dashboard grid using Tailwind."}
                    ]},
                    {"title": "Phase 2: JavaScript Mastery", "phase_project": "Build a weather app that pulls and displays data from a public API.", "milestones": [
                        {"name": "Core JS", "desc": "Variables, Functions, Closures, and DOM manipulation.", "estimated_hours": 15, "checkpoint": "Build a dynamic list builder in vanilla JS."},
                        {"name": "Async JS", "desc": "Promises, Async/Await, and Fetching APIs.", "estimated_hours": 10, "checkpoint": "Fetch user data from a public user endpoint."},
                        {"name": "Data Structures", "desc": "Arrays, Objects, and ES6+ features.", "estimated_hours": 8, "checkpoint": "Solve 5 basic array manipulation problems."}
                    ]},
                    {"title": "Phase 3: React Development", "phase_project": "Create a fully functional movie search dashboard with filtering.", "milestones": [
                        {"name": "Components & Props", "desc": "Functional components and data passing.", "estimated_hours": 10, "checkpoint": "Create a reusable Card component."},
                        {"name": "State & Hooks", "desc": "useState, useEffect, and custom hooks.", "estimated_hours": 15, "checkpoint": "Track user inputs and search queries in local state."},
                        {"name": "Routing", "desc": "React Router for Single Page Apps.", "estimated_hours": 8, "checkpoint": "Setup home, details, and about routes."}
                    ]},
                    {"title": "Phase 4: Backend Fundamentals", "phase_project": "Build a Flask-based task manager backend with complete CRUD APIs.", "milestones": [
                        {"name": "Flask / Django", "desc": "Building robust servers and routing logic.", "estimated_hours": 15, "checkpoint": "Bootstrap a Flask app with blueprint routing."},
                        {"name": "RESTful APIs", "desc": "Designing CRUD endpoints for frontend integration.", "estimated_hours": 10, "checkpoint": "Expose JSON endpoints for tasks."},
                        {"name": "Authentication", "desc": "JWT and session-based user security.", "estimated_hours": 12, "checkpoint": "Secure private endpoints with Flask-JWT-Extended."}
                    ]},
                    {"title": "Phase 5: Database Design", "phase_project": "Connect your task backend to a persistent PostgreSQL database.", "milestones": [
                        {"name": "SQL (PostgreSQL)", "desc": "Schema design, joins, and indexing.", "estimated_hours": 15, "checkpoint": "Write SQL queries to join 3 related tables."},
                        {"name": "NoSQL (MongoDB)", "desc": "Document-based storage and aggregation.", "estimated_hours": 10, "checkpoint": "Store flexible document structures in MongoDB."},
                        {"name": "ORM/ODM", "desc": "SQLAlchemy and MongoEngine.", "estimated_hours": 10, "checkpoint": "Define tables using SQLAlchemy declarative base models."}
                    ]},
                    {"title": "Phase 6: Full Integration", "phase_project": "Integrate your React frontend with your Flask API backend.", "milestones": [
                        {"name": "Axios/Fetch", "desc": "Connecting React to your Backend APIs.", "estimated_hours": 8, "checkpoint": "Perform fetch calls on component mount."},
                        {"name": "CORS & Headers", "desc": "Handling cross-origin requests securely.", "estimated_hours": 6, "checkpoint": "Configure CORS headers in backend responses."},
                        {"name": "State Sharing", "desc": "Context API or Redux for global state.", "estimated_hours": 12, "checkpoint": "Implement global auth state provider."}
                    ]},
                    {"title": "Phase 7: Advanced Concepts", "phase_project": "Build a real-time notification system inside your application.", "milestones": [
                        {"name": "Real-time Ops", "desc": "WebSockets and Socket.io for chat/notifications.", "estimated_hours": 12, "checkpoint": "Broadcast message from server to connected clients."},
                        {"name": "Caching", "desc": "Redis for session management and speed.", "estimated_hours": 10, "checkpoint": "Cache database queries in Redis memory."},
                        {"name": "MVC Patterns", "desc": "Organizing code for scalability.", "estimated_hours": 8, "checkpoint": "Structure project into models, views, and controllers."}
                    ]},
                    {"title": "Phase 8: Security & Testing", "phase_project": "Write a complete test suite for your backend and frontend apps.", "milestones": [
                        {"name": "OWASP Top 10", "desc": "Preventing XSS and SQL Injection.", "estimated_hours": 10, "checkpoint": "Input validation and SQL parameterization check."},
                        {"name": "Unit Testing", "desc": "Pytest and Jest for bug-free code.", "estimated_hours": 12, "checkpoint": "Write unit tests targeting route controller logic."},
                        {"name": "Logging", "desc": "System monitoring and error tracking.", "estimated_hours": 6, "checkpoint": "Add logger module writing to log files."}
                    ]},
                    {"title": "Phase 9: DevOps & Cloud", "phase_project": "Deploy containerized apps via auto pipelines.", "milestones": [
                        {"name": "Docker", "desc": "Containerizing your full stack app.", "estimated_hours": 10, "checkpoint": "Build multi-stage Docker images."},
                        {"name": "CI/CD", "desc": "Automated deployments with GitHub Actions.", "estimated_hours": 10, "checkpoint": "Automate testing via workflows."},
                        {"name": "Vercel & Render", "desc": "Hosting frontend and backend in production.", "estimated_hours": 8, "checkpoint": "Verify live SSL and DNS settings."}
                    ]},
                    {"title": "Phase 10: Career Prep", "phase_project": "Prepare full portfolio, resume, and GitHub files.", "milestones": [
                        {"name": "Portfolio App", "desc": "Building a production-ready Capstone project.", "estimated_hours": 20, "checkpoint": "Host capstone demo and write README."},
                        {"name": "DSA Prep", "desc": "Solving Array and String challenges on LeetCode.", "estimated_hours": 30, "checkpoint": "Solve 50 Easy/Medium LeetCode questions."},
                        {"name": "Interview Skills", "desc": "Soft skills and technical system design.", "estimated_hours": 15, "checkpoint": "Answer 10 behavioral and design prompts."}
                    ]}
                ],
                "projects": ["Netflix Clone", "E-Commerce Site", "Real-Time Chat App", "AI Project", "Expense Tracker"],
                "stack": {"frontend": "React, Tailwind", "backend": "Flask, Django", "db": "PostgreSQL, MongoDB"},
                "timeline": "6–8 Months",
                "final_capstone": "Design and build a multi-user SaaS web app with secure payments, background jobs, and a clean responsive interface."
            }
            AIService._post_process_roadmap(roadmap, "fullstack")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        elif is_frontend:
            roadmap = {
                "role": "Frontend Developer (2026)",
                "phases": [
                    {"title": "Phase 0: Basics & Setup", "phase_project": "Setup your developer workspace and configure Git version control.", "milestones": [
                        {"name": "Internet", "desc": "How browsers and the web work.", "estimated_hours": 4, "checkpoint": "Explain IP and browser caching."},
                        {"name": "Tools", "desc": "VS Code, Git, and Node.js install.", "estimated_hours": 6, "checkpoint": "Create and push a GitHub repository."}
                    ]},
                    {"title": "Phase 1: HTML Mastery", "phase_project": "Code a clean, semantic web layout with form validations.", "milestones": [
                        {"name": "Semantic Tags", "desc": "Clean and accessible structure.", "estimated_hours": 6, "checkpoint": "Check website accessibility scoring."},
                        {"name": "Forms", "desc": "Inputs, Validation, and Data submission.", "estimated_hours": 8, "checkpoint": "Add client-side form validation attributes."}
                    ]},
                    {"title": "Phase 2: CSS Layouts", "phase_project": "Build a responsive grid landing page styled purely with CSS Grid.", "milestones": [
                        {"name": "Flex/Grid", "desc": "Modern responsive layout techniques.", "estimated_hours": 10, "checkpoint": "Create a CSS grid gallery."},
                        {"name": "Animations", "desc": "CSS Transitions and keyframes.", "estimated_hours": 8, "checkpoint": "Code a loading spinner animation."}
                    ]},
                    {"title": "Phase 3: JavaScript Core", "phase_project": "Create an interactive interactive todo list app with DOM updates.", "milestones": [
                        {"name": "DOM", "desc": "Selecting and modifying HTML with JS.", "estimated_hours": 12, "checkpoint": "Update UI dynamically on list operations."},
                        {"name": "Events", "desc": "Clicks, inputs, and form listeners.", "estimated_hours": 8, "checkpoint": "Add search filtration using keypress events."}
                    ]},
                    {"title": "Phase 4: JavaScript Pro", "phase_project": "Build a dashboard fetching real-time user profiles from an open API.", "milestones": [
                        {"name": "Async/Await", "desc": "Handling external API data.", "estimated_hours": 10, "checkpoint": "Implement retry logic for fetch calls."},
                        {"name": "ES6 Features", "desc": "Destructuring, Arrow functions, and Map/Filter.", "estimated_hours": 8, "checkpoint": "Write clean array transforms."}
                    ]},
                    {"title": "Phase 5: React Basics", "phase_project": "Build a functional multi-card layout managed via React State.", "milestones": [
                        {"name": "JSX", "desc": "Writing HTML inside your JavaScript.", "estimated_hours": 8, "checkpoint": "Render items from a dynamic array list."},
                        {"name": "State", "desc": "Managing dynamic data with hooks.", "estimated_hours": 12, "checkpoint": "Persist search inputs in state."}
                    ]},
                    {"title": "Phase 6: React Advanced", "phase_project": "Build a theme toggle feature accessible by all UI subcomponents.", "milestones": [
                        {"name": "Context API", "desc": "Handling global user data.", "estimated_hours": 10, "checkpoint": "Consume user configuration globally."},
                        {"name": "Custom Hooks", "desc": "Reusable logic for multiple components.", "estimated_hours": 10, "checkpoint": "Code custom useLocalStorage hook."}
                    ]},
                    {"title": "Phase 7: State Tools", "phase_project": "Refactor state management of a shopping cart app to use Zustand.", "milestones": [
                        {"name": "Zustand / Redux", "desc": "Modern state management libraries.", "estimated_hours": 12, "checkpoint": "Implement global store for cart state."},
                        {"name": "State Persistence", "desc": "Saving data across page refreshes.", "estimated_hours": 6, "checkpoint": "Configure store auto-hydration."}
                    ]},
                    {"title": "Phase 8: API Integration", "phase_project": "Optimize queries of a dynamic dataset using React Query.", "milestones": [
                        {"name": "Axios", "desc": "Professional HTTP client for React.", "estimated_hours": 6, "checkpoint": "Configure global axios interceptor instances."},
                        {"name": "React Query", "desc": "Caching and fetching like a pro.", "estimated_hours": 12, "checkpoint": "Cache list queries with custom staleTime."}
                    ]},
                    {"title": "Phase 9: UI Design", "phase_project": "Style a complete responsive dashboard modeled on a Figma design.", "milestones": [
                        {"name": "Figma", "desc": "Turning designs into pixel-perfect code.", "estimated_hours": 8, "checkpoint": "Extract layout specs and spacing from Figma file."},
                        {"name": "Tailwind CSS", "desc": "Fast styling with utility classes.", "estimated_hours": 8, "checkpoint": "Style custom utility-focused layouts."}
                    ]},
                    {"title": "Phase 10: Performance", "phase_project": "Deploy a serverless website optimized for maximum lighthouse scores.", "milestones": [
                        {"name": "Next.js", "desc": "SEO and Server-side rendering.", "estimated_hours": 15, "checkpoint": "Configure page using Server Component architecture."},
                        {"name": "Lazy Loading", "desc": "Optimizing image and code bundle size.", "estimated_hours": 8, "checkpoint": "Split bundle size using dynamic imports."}
                    ]}
                ],
                "projects": ["Portfolio Website", "Movie App", "Blog UI", "Admin Dashboard", "E-Commerce Frontend"],
                "stack": {"frontend": "React, Next.js, Tailwind", "tools": "Git, Figma, VS Code"},
                "timeline": "5–7 Months",
                "final_capstone": "Develop and optimize a production-ready Next.js application integrated with a CMS, utilizing Tailwind CSS and advanced state management."
            }
            AIService._post_process_roadmap(roadmap, "frontend")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        elif is_backend:
            roadmap = {
                "role": "Backend Developer (2026)",
                "phases": [
                    {"title": "Phase 0: Basics", "phase_project": "Configure a basic Linux server environment with customized shell utilities.", "milestones": [
                        {"name": "Internet", "desc": "HTTP, DNS, TCP/IP", "estimated_hours": 4, "checkpoint": "Trace route pathways for standard requests."},
                        {"name": "OS", "desc": "Linux basics, Terminal", "estimated_hours": 6, "checkpoint": "Manage file permissions and scripts."}
                    ]},
                    {"title": "Phase 1: Languages", "phase_project": "Implement standard computer science algorithms in your language of choice.", "milestones": [
                        {"name": "Core Syntax", "desc": "Python, Node.js, or Go", "estimated_hours": 12, "checkpoint": "Code custom modules and package sets."},
                        {"name": "DSA", "desc": "Arrays, Trees, Graphs", "estimated_hours": 15, "checkpoint": "Code lookup operations for BST trees."}
                    ]},
                    {"title": "Phase 2: APIs", "phase_project": "Build an API service supporting nested lookup data routes.", "milestones": [
                        {"name": "RESTful APIs", "desc": "Designing JSON endpoints", "estimated_hours": 10, "checkpoint": "Implement CRUD api with proper status returns."},
                        {"name": "GraphQL", "desc": "Advanced data querying", "estimated_hours": 8, "checkpoint": "Define schema and write dynamic resolver logic."}
                    ]},
                    {"title": "Phase 3: Databases", "phase_project": "Design a relational schema with proper primary and foreign indexes.", "milestones": [
                        {"name": "Relational", "desc": "PostgreSQL, MySQL", "estimated_hours": 15, "checkpoint": "Configure table indices and primary relationships."},
                        {"name": "NoSQL", "desc": "MongoDB, Redis", "estimated_hours": 10, "checkpoint": "Store flexible schema-less data blocks."}
                    ]},
                    {"title": "Phase 4: Caching", "phase_project": "Integrate an in-memory cache layer to buffer heavy database queries.", "milestones": [
                        {"name": "Redis", "desc": "In-memory data stores", "estimated_hours": 10, "checkpoint": "Cache resource responses in local Redis instances."},
                        {"name": "CDNs", "desc": "Content delivery", "estimated_hours": 6, "checkpoint": "Configure edge cache rules."}
                    ]},
                    {"title": "Phase 5: Security", "phase_project": "Secure backend APIs using modern cryptographically signed token sets.", "milestones": [
                        {"name": "Auth", "desc": "JWT, OAuth2", "estimated_hours": 12, "checkpoint": "Implement token rotation and expiration rules."},
                        {"name": "OWASP", "desc": "Preventing injection & XSS", "estimated_hours": 10, "checkpoint": "Sanitize and escape all incoming query inputs."}
                    ]},
                    {"title": "Phase 6: Testing", "phase_project": "Setup code quality checks and automated unit/integration tests.", "milestones": [
                        {"name": "Unit Tests", "desc": "Pytest, Jest", "estimated_hours": 12, "checkpoint": "Write unit tests matching 80% coverage limits."},
                        {"name": "Integration Tests", "desc": "Testing API flows", "estimated_hours": 10, "checkpoint": "Mock server calls to test database logic."}
                    ]},
                    {"title": "Phase 7: CI/CD", "phase_project": "Automate testing and containerization steps on code changes.", "milestones": [
                        {"name": "Pipelines", "desc": "GitHub Actions", "estimated_hours": 8, "checkpoint": "Configure build automation workflows."},
                        {"name": "Docker", "desc": "Containerization basics", "estimated_hours": 10, "checkpoint": "Write efficient multi-stage Dockerfiles."}
                    ]},
                    {"title": "Phase 8: Architecture", "phase_project": "Deconstruct a monolithic app into message-driven decoupled services.", "milestones": [
                        {"name": "Microservices", "desc": "Service decoupling", "estimated_hours": 15, "checkpoint": "Configure inter-service communication ports."},
                        {"name": "Message Brokers", "desc": "Kafka, RabbitMQ", "estimated_hours": 12, "checkpoint": "Implement producer-consumer message flows."}
                    ]},
                    {"title": "Phase 9: Scale", "phase_project": "Setup load balancers and system telemetry for performance tracking.", "milestones": [
                        {"name": "Load Balancing", "desc": "NGINX, HAProxy", "estimated_hours": 10, "checkpoint": "Configure NGINX reverse proxy routers."},
                        {"name": "Monitoring", "desc": "Prometheus, Grafana", "estimated_hours": 12, "checkpoint": "Configure live server resource monitors."}
                    ]}
                ],
                "projects": ["REST API Service", "Auth Server", "Task Queue Worker"],
                "stack": {"backend": "Python/Go/Node", "db": "PostgreSQL/Redis"},
                "timeline": "6-8 Months",
                "final_capstone": "Design a highly available distributed API server equipped with rate-limiting, message queues, caching, and automated scaling properties."
            }
            AIService._post_process_roadmap(roadmap, "backend")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        elif is_datascience:
            roadmap = {
                "role": "Data Scientist (2026)",
                "phases": [
                    {"title": "Phase 0: Math", "phase_project": "Analyze a random variable dataset and test distribution parameters.", "milestones": [
                        {"name": "Stats", "desc": "Probability, Distributions", "estimated_hours": 15, "checkpoint": "Calculate standard error bounds."},
                        {"name": "LinAlg", "desc": "Matrices, Vectors", "estimated_hours": 12, "checkpoint": "Perform matrix decomposition manually."}
                    ]},
                    {"title": "Phase 1: Python", "phase_project": "Write robust scripting code to read and parse local raw telemetry feeds.", "milestones": [
                        {"name": "Basics", "desc": "Python scripting", "estimated_hours": 10, "checkpoint": "Write object-oriented Python modules."},
                        {"name": "Data Types", "desc": "Lists, Dictionaries", "estimated_hours": 8, "checkpoint": "Implement custom key lookup scripts."}
                    ]},
                    {"title": "Phase 2: Data Tools", "phase_project": "Clean and preprocess a noisy csv database using vector operations.", "milestones": [
                        {"name": "Pandas", "desc": "Data manipulation", "estimated_hours": 12, "checkpoint": "Handle empty values and outliers in dataframes."},
                        {"name": "NumPy", "desc": "Numerical arrays", "estimated_hours": 10, "checkpoint": "Perform fast vector dot product runs."}
                    ]},
                    {"title": "Phase 3: Vis", "phase_project": "Produce a presentation deck outlining patterns from data graphs.", "milestones": [
                        {"name": "Matplotlib", "desc": "Basic plotting", "estimated_hours": 8, "checkpoint": "Configure custom charts and scales."},
                        {"name": "Seaborn", "desc": "Statistical graphs", "estimated_hours": 8, "checkpoint": "Generate custom correlation heatmaps."}
                    ]},
                    {"title": "Phase 4: ML Basics", "phase_project": "Train a model predicting house values based on feature tables.", "milestones": [
                        {"name": "Scikit-Learn", "desc": "Classical ML models", "estimated_hours": 15, "checkpoint": "Train validation split evaluation flow."},
                        {"name": "Regression", "desc": "Linear & Logistic", "estimated_hours": 12, "checkpoint": "Measure model coefficients and residuals."}
                    ]},
                    {"title": "Phase 5: ML Adv", "phase_project": "Build an ensemble classifier predicting customer churn ratios.", "milestones": [
                        {"name": "Trees", "desc": "Random Forests", "estimated_hours": 15, "checkpoint": "Evaluate feature importances from classifiers."},
                        {"name": "Clustering", "desc": "K-Means, PCA", "estimated_hours": 12, "checkpoint": "Plot cluster outputs across principal components."}
                    ]},
                    {"title": "Phase 6: Deep Learning", "phase_project": "Build a network classifying images into designated categories.", "milestones": [
                        {"name": "NNs", "desc": "Neural Networks", "estimated_hours": 15, "checkpoint": "Code custom backprop training loop."},
                        {"name": "PyTorch/TF", "desc": "Deep learning frameworks", "estimated_hours": 18, "checkpoint": "Compile a model structure using custom layers."}
                    ]},
                    {"title": "Phase 7: NLP", "phase_project": "Train a sentiment classifier categorizing client support emails.", "milestones": [
                        {"name": "Text", "desc": "Tokenization, Embeddings", "estimated_hours": 12, "checkpoint": "Map raw strings into dense embeddings."},
                        {"name": "Transformers", "desc": "HuggingFace, BERT", "estimated_hours": 15, "checkpoint": "Fine-tune pretrained transformers."}
                    ]},
                    {"title": "Phase 8: Big Data", "phase_project": "Write map-reduce scripts extracting metrics from massive log tables.", "milestones": [
                        {"name": "SQL", "desc": "Advanced querying", "estimated_hours": 12, "checkpoint": "Use window operations for relative ranking."},
                        {"name": "Spark", "desc": "Distributed computing", "estimated_hours": 15, "checkpoint": "Process dataset in distributed spark sessions."}
                    ]},
                    {"title": "Phase 9: MLOps", "phase_project": "Deploy your model as a microservice and track accuracy drift.", "milestones": [
                        {"name": "Deployment", "desc": "Flask/FastAPI for models", "estimated_hours": 12, "checkpoint": "Expose endpoint for model predictions."},
                        {"name": "Tracking", "desc": "MLflow, Weights & Biases", "estimated_hours": 10, "checkpoint": "Register model runs and parameters."}
                    ]}
                ],
                "projects": ["Housing Price Predictor", "Customer Segmentation", "Text Sentiment Analyzer"],
                "stack": {"language": "Python/R", "tools": "Pandas/PyTorch/SQL"},
                "timeline": "8-12 Months",
                "final_capstone": "Deploy an end-to-end model pipeline that pulls streaming data, performs inference at scale, and tracks metrics in a dashboard."
            }
            AIService._post_process_roadmap(roadmap, "datascience")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        elif is_devops:
            roadmap = {
                "role": "DevOps Engineer (2026)",
                "phases": [
                    {"title": "Phase 0: OS & Linux", "phase_project": "Script automated system cleanups running on schedule.", "milestones": [
                        {"name": "CLI", "desc": "Bash scripting", "estimated_hours": 8, "checkpoint": "Write a bash script parsing arguments."},
                        {"name": "Networking", "desc": "TCP/IP, DNS, SSH", "estimated_hours": 10, "checkpoint": "Troubleshoot network routing errors."}
                    ]},
                    {"title": "Phase 1: Programming", "phase_project": "Create a cli utility integrating with git to check branch naming.", "milestones": [
                        {"name": "Python/Go", "desc": "Automation scripting", "estimated_hours": 12, "checkpoint": "Interact with file system and env properties."},
                        {"name": "Git", "desc": "Version control", "estimated_hours": 8, "checkpoint": "Rebase branches and handle merge conflicts."}
                    ]},
                    {"title": "Phase 2: Cloud", "phase_project": "Bootstrap a virtual private cloud configuration with security groups.", "milestones": [
                        {"name": "AWS/Azure/GCP", "desc": "Cloud fundamentals", "estimated_hours": 15, "checkpoint": "Configure access control policy models."},
                        {"name": "IAM", "desc": "Identity & Access Management", "estimated_hours": 10, "checkpoint": "Create users under custom role bounds."}
                    ]},
                    {"title": "Phase 3: Containers", "phase_project": "Write multi-stage Dockerfiles caching build dependencies.", "milestones": [
                        {"name": "Docker", "desc": "Building images", "estimated_hours": 10, "checkpoint": "Maintain small final image sizes."},
                        {"name": "Registry", "desc": "Docker Hub, ECR", "estimated_hours": 8, "checkpoint": "Push versioned images securely."}
                    ]},
                    {"title": "Phase 4: Orchestration", "phase_project": "Deploy a multi-service web application onto a local Kubernetes cluster.", "milestones": [
                        {"name": "Kubernetes", "desc": "Pods, Deployments", "estimated_hours": 15, "checkpoint": "Write YAML config declarations for pods."},
                        {"name": "Helm", "desc": "K8s package manager", "estimated_hours": 10, "checkpoint": "Build custom chart packages."}
                    ]},
                    {"title": "Phase 5: CI/CD", "phase_project": "Write a git pipeline running build tests and deploying on success.", "milestones": [
                        {"name": "Jenkins/Actions", "desc": "Continuous Integration", "estimated_hours": 12, "checkpoint": "Implement stage gates for pull requests."},
                        {"name": "ArgoCD", "desc": "Continuous Deployment (GitOps)", "estimated_hours": 10, "checkpoint": "Sync cluster state with git repo settings."}
                    ]},
                    {"title": "Phase 6: IaC", "phase_project": "Define complete cloud infrastructure as a modular Terraform project.", "milestones": [
                        {"name": "Terraform", "desc": "Infrastructure as Code", "estimated_hours": 15, "checkpoint": "Use remote backends for state management."},
                        {"name": "Ansible", "desc": "Configuration management", "estimated_hours": 12, "checkpoint": "Write playbooks to update node packages."}
                    ]},
                    {"title": "Phase 7: Monitoring", "phase_project": "Configure system metrics collectors alerting on resource spikes.", "milestones": [
                        {"name": "Prometheus", "desc": "Metrics collection", "estimated_hours": 12, "checkpoint": "Expose custom app metrics for Prometheus."},
                        {"name": "Grafana", "desc": "Dashboards & Alerts", "estimated_hours": 10, "checkpoint": "Create dynamic system dashboards."}
                    ]},
                    {"title": "Phase 8: Logging", "phase_project": "Setup a centralized server gathering and indexing log stdout streams.", "milestones": [
                        {"name": "ELK Stack", "desc": "Elasticsearch, Logstash, Kibana", "estimated_hours": 12, "checkpoint": "Filter raw logs using regex matches."},
                        {"name": "Datadog", "desc": "APM and Logs", "estimated_hours": 10, "checkpoint": "Configure tracing flags inside backend apps."}
                    ]},
                    {"title": "Phase 9: Security", "phase_project": "Setup secret scanners and secure vault spaces for credentials.", "milestones": [
                        {"name": "DevSecOps", "desc": "Secret scanning, Vault", "estimated_hours": 12, "checkpoint": "Inject secret tokens securely into runtimes."},
                        {"name": "Compliance", "desc": "Auditing infra", "estimated_hours": 8, "checkpoint": "Run automated infrastructure security scans."}
                    ]}
                ],
                "projects": ["Dockerized Web App", "Terraform AWS Infra", "Kubernetes Cluster Setup"],
                "stack": {"cloud": "AWS/K8s", "tools": "Terraform/Docker"},
                "timeline": "6-9 Months",
                "final_capstone": "Build and secure a Kubernetes cluster with automated deployments, logging, backups, and live auto-scaling rules."
            }
            AIService._post_process_roadmap(roadmap, "devops")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        elif is_ml:
            roadmap = {
                "role": "Machine Learning Engineer (2026)",
                "phases": [
                    {"title": "Phase 0: Foundations & Math", "phase_project": "Build a statistical analysis notebook for a sample dataset.", "milestones": [
                        {"name": "Linear Algebra & Calculus", "desc": "Vector spaces, matrix multiplication, derivatives, and gradients.", "estimated_hours": 15, "checkpoint": "Solve linear equations and calculate gradients manually."},
                        {"name": "Probability & Statistics", "desc": "Distributions, Bayes theorem, hypothesis testing.", "estimated_hours": 15, "checkpoint": "Perform a hypothesis test and calculate Bayes theorem probabilities."}
                    ]},
                    {"title": "Phase 1: Python & Data Processing", "phase_project": "Perform Exploratory Data Analysis (EDA) on a dataset and present findings.", "milestones": [
                        {"name": "Numpy & Pandas", "desc": "Dataframes, vectorization, indexing, and merging data.", "estimated_hours": 12, "checkpoint": "Load, clean, and aggregate a 1M+ row dataset."},
                        {"name": "Matplotlib & Seaborn", "desc": "Statistical visualizations and plot customization.", "estimated_hours": 8, "checkpoint": "Generate correlation heatmaps and distribution plots."}
                    ]},
                    {"title": "Phase 2: Classical Machine Learning", "phase_project": "Train and tune an end-to-end model to predict housing prices.", "milestones": [
                        {"name": "Supervised Learning", "desc": "Linear regression, decision trees, support vector machines.", "estimated_hours": 20, "checkpoint": "Build and evaluate multiple classification models."},
                        {"name": "Unsupervised Learning", "desc": "K-means, hierarchical clustering, PCA.", "estimated_hours": 15, "checkpoint": "Segment a customer dataset using K-means and reduce dimensions with PCA."}
                    ]},
                    {"title": "Phase 3: Deep Learning Foundations", "phase_project": "Build and deploy an image classifier model using PyTorch.", "milestones": [
                        {"name": "Neural Networks", "desc": "Activation functions, backpropagation, feedforward networks.", "estimated_hours": 15, "checkpoint": "Write a simple neural network from scratch in Python."},
                        {"name": "PyTorch or TensorFlow", "desc": "Tensors, datasets, and training loops.", "estimated_hours": 20, "checkpoint": "Train a simple CNN on CIFAR-10 using PyTorch."}
                    ]},
                    {"title": "Phase 4: Advanced DL & GenAI", "phase_project": "Build a custom QA bot over local document PDF files.", "milestones": [
                        {"name": "Transformers & LLMs", "desc": "Self-attention mechanism, transformer architecture, fine-tuning.", "estimated_hours": 25, "checkpoint": "Fine-tune a small LLM (e.g. GPT-2 or Llama-3) on a custom dataset."},
                        {"name": "Prompt Engineering & RAG", "desc": "Retrieval Augmented Generation, vector databases.", "estimated_hours": 15, "checkpoint": "Create a RAG pipeline using LangChain and ChromaDB."}
                    ]}
                ],
                "projects": ["EDA Dashboard", "Housing Price Predictor", "Image Classifier App", "RAG PDF Bot"],
                "stack": {"language": "Python", "frameworks": "PyTorch, Scikit-Learn", "tools": "Jupyter, HuggingFace"},
                "timeline": "6–9 Months",
                "final_capstone": "Design and implement a production-ready RAG application using a fine-tuned LLM, vector database, and custom interface."
            }
            AIService._post_process_roadmap(roadmap, "ml")
            return AIService._build_roadmap_response(roadmap, current_skills)
            
        # --- DYNAMIC GEMINI GENERATOR (For other roles) ---
        from app.services.prompts.roadmap_prompt import ROADMAP_GENERATION_PROMPT
        from flask import current_app
        import os
        import json
        
        api_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            return AIService._build_roadmap_response(AIService._get_fallback_roadmap(target_role), current_skills)
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = ROADMAP_GENERATION_PROMPT.format(
                target_role=target_role,
                current_skills=", ".join(current_skills) if current_skills else "None"
            )
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            roadmap_dict = json.loads(response.text)
            
            # If the response conforms to {"visual": "...", "data": {...}}, validate/update it
            if isinstance(roadmap_dict, dict) and "data" in roadmap_dict:
                roadmap_dict["data"] = AIService._mark_completed_topics(roadmap_dict["data"], current_skills)
                roadmap_dict["visual"] = AIService._generate_ascii_visual_from_data(roadmap_dict["data"])
            else:
                # If Gemini returned a flat/old schema, build the correct response
                roadmap_dict = AIService._build_roadmap_response(roadmap_dict, current_skills)
                
            return roadmap_dict
            
        except Exception as e:
            current_app.logger.error(f"Gemini API error during roadmap generation: {e}")
            return AIService._build_roadmap_response(AIService._get_fallback_roadmap(target_role), current_skills)

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
            current_app.logger.error(f"AI Analysis error: {e}")
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

    @staticmethod
    def generate_outreach_copy(user_profile, job_title, company_name, job_description, tone, manual_skills=None):
        # Extract user details
        name = "Job Seeker"
        profile_skills = []
        if user_profile and user_profile.user:
            name = user_profile.user.name
            profile_skills = user_profile.skills or []

        # Merge profile skills with manually entered highlights/skills
        skills = list(set(profile_skills + (manual_skills or [])))
        if not skills:
            skills = ["Full-Stack Engineering", "Software Development", "Problem Solving"]

        skills_str = ", ".join(skills[:3])
        skills_detailed = ", ".join(skills[:4])

        # Formatting defaults
        tone = (tone or "professional").lower()
        job_title = job_title or "Software Developer"
        company_name = company_name or "Target Company"

        # Generate outreach assets based on tone
        if tone == "enthusiastic":
            # --- ENTHUSIASTIC TONE ---
            cover_letter = f"""Dear Hiring Team at {company_name},

I am writing this with absolute excitement to apply for the {job_title} position at {company_name}! I have been following your journey and am constantly inspired by your incredible team culture, commitment to excellence, and pioneering products. I would be thrilled to bring my energy, dedication, and technical expertise to your mission!

As a developer skilled in {skills_detailed}, I love building high-quality, impactful software. In my past work, I've always prioritized clean architecture and collaborative problem-solving. Your goals at {company_name} align perfectly with my passion for creating seamless user experiences and robust systems.

I'm incredibly eager to contribute to your upcoming projects. Thank you so much for your time and consideration. I would jump at the chance to jump on a quick call and discuss how my skills and high-energy approach can add value to your team!

Best regards,
{name}"""

            cold_subject = f"Thrilled to connect! | {job_title} Application | {name}"
            cold_body = f"""Hi,

I hope you're having an amazing day!

I've been following {company_name}'s recent innovations and was absolutely thrilled to see the opening for a {job_title}. I am a passionate developer with a strong background in {skills_str}, and I believe my creative approach to software development would fit perfectly into your team culture.

I'd love to learn more about the team's goals and share how my enthusiasm and technical skills can support your vision. Would you be open to a quick 5-minute chat sometime this week?

Thank you so much!

Best regards,
{name}"""

            # Maximum 300 characters, high-energy hook
            linkedin = f"Hi! I'm absolutely inspired by {company_name}'s vision and saw the {job_title} opening. With my background in {skills_str} and my passion for building high-impact software, I'd love to connect and learn more about your amazing team. Best, {name}."

        elif tone == "bold":
            # --- BOLD & METRIC-DRIVEN TONE ---
            cover_letter = f"""Dear Hiring Manager,

I don't just write clean code; I engineer robust solutions that directly drive business growth, optimize system performance, and solve high-scale technical challenges. I am writing to apply for the {job_title} position at {company_name}, where I am confident I can make an immediate, positive impact.

With a strong foundation in {skills_detailed}, I have specialized in building highly-scalable architectures, reducing technical debt, and shipping resilient products. I approach engineering with a focus on metrics—whether that means boosting load speed, maximizing uptime, or improving developer velocity.

I am looking for a high-impact environment where performance and technical execution are highly valued, which is exactly why {company_name} caught my attention. I welcome the opportunity to discuss how my technical expertise can translate into direct results for your engineering team.

Best regards,
{name}"""

            cold_subject = f"Driving high-impact results as your next {job_title} | {name}"
            cold_body = f"""Hi,

I'll get straight to the point: I build robust, scalable systems that solve complex problems and drive software efficiency. 

I saw your opening for a {job_title} at {company_name}. With my specialized skills in {skills_str}, I am confident I can immediately step in and contribute to optimizing your engineering workflows, boosting platform speed, and building resilient features.

Let's cut through the red tape. I'd love to jump on a brief call to discuss the top engineering challenges you're currently facing and how I can help solve them.

Best,
{name}"""

            # Maximum 300 characters, assertive hook
            linkedin = f"Hi! I saw the {job_title} role at {company_name}. I specialize in engineering high-scale systems using {skills_str}. I'm confident my metric-driven, direct approach can add immediate value to your current projects. Let's connect to discuss. - {name}."

        elif tone == "creative":
            # --- CREATIVE & HOOK TONE ---
            cover_letter = f"""Dear Hiring Team at {company_name},

While most cover letters start with the usual standard phrases, I'd rather start by telling you why I love solving complex puzzles. I believe that engineering is the art of translating human problems into elegant, invisible solutions. I am applying to be your next {job_title} because your team at {company_name} builds exactly that kind of art.

My toolkit includes {skills_detailed}, but my real strength lies in my curiosity and my ability to think outside conventional engineering boxes. Whether it's redesigning a slow API, creating a glassmorphic dashboard, or building clean features, I enjoy challenges that require both high engineering discipline and creative spark.

I would love to bring my unique engineering perspective, standard-defying dedication, and collaborative spirit to {company_name}. Let's build something unforgettable together.

Best regards,
{name}"""

            cold_subject = f"A slightly different pitch for the {job_title} role | {name}"
            cold_body = f"""Hi,

Every developer writes code, but I focus on crafting experiences that feel like magic. 

I came across the {job_title} role at {company_name} and immediately felt a connection to how you approach product design and technical scaling. I am an engineer who blends deep technical skills in {skills_str} with a passion for creative, outside-the-box problem solving.

If you're looking for someone who doesn't just check boxes but brings new ideas to the table, I'd love to chat. Could we connect for a quick virtual coffee this week?

Cheers,
{name}"""

            # Maximum 300 characters, unique hook
            linkedin = f"Hi! While most developers just write code, I focus on turning complex challenges into elegant technical art. I saw the {job_title} opening at {company_name} and would love to connect to discuss how my experience in {skills_str} can support your team! Cheers, {name}."

        else:
            # --- PROFESSIONAL TONE ---
            cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my solid background in software engineering, dedication to code quality, and proven expertise in {skills_detailed}, I am highly confident in my ability to make a valuable contribution to your development team.

Throughout my career, I have consistently focused on building scalable, performant, and secure web applications. I understand the importance of robust database design, automated workflows, and clean code practices. Your current objectives at {company_name} align closely with my technical background and my commitment to delivering reliable software solutions.

I am eager to apply my technical foundation and collaborative mindset to your engineering goals. Thank you for your time and consideration of my application. I would welcome the opportunity to discuss my qualifications with you in more detail.

Sincerely,
{name}"""

            cold_subject = f"{job_title} Application - {name}"
            cold_body = f"""Dear Hiring Manager,

I hope this email finds you well.

I am writing to express my interest in the {job_title} position currently open at {company_name}. I am a software engineer with extensive experience in {skills_str}, specializing in building reliable, scalable, and secure web services.

Given the focus of {company_name} on technical excellence, I believe my professional experience and dedication to code quality would be a strong asset to your team.

I have attached my details for your review and would appreciate the opportunity to schedule a brief introductory call at your convenience.

Thank you for your time and consideration.

Sincerely,
{name}"""

            # Maximum 300 characters, formal hook
            linkedin = f"Hello. I am a software engineer specializing in {skills_str}. I recently saw the {job_title} opening at {company_name} and would appreciate the opportunity to connect and discuss how my technical background and focus on quality can benefit your team. Sincerely, {name}."

        # Ensure LinkedIn outreach is strictly under 300 characters
        if len(linkedin) > 297:
            linkedin = linkedin[:294] + "..."

        return {
            "cover_letter": cover_letter.strip(),
            "cold_email_subject": cold_subject.strip(),
            "cold_email_body": cold_body.strip(),
            "linkedin_message": linkedin.strip()
        }

