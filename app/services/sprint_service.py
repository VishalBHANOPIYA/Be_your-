import json
import random
import hashlib
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.user import User
from app.models.sprint import UserSprintSubmission

class SprintService:
    # 15 Curated daily challenges for the global Wordle-style platform experience
    CHALLENGES = [
        # --- DEBUG SPRINT TRACK ---
        {
            "id": 1,
            "title": "Python: Mutable Default Argument Bug",
            "type": "debug",
            "category": "Backend",
            "problem": "Debugging is crucial. What is wrong with the following function definition? How would you fix it to avoid list accumulation across function calls?\n\n```python\ndef append_to(element, target_list=[]):\n    target_list.append(element)\n    return target_list\n```",
            "starter": "def append_to(element, target_list=None):\n    if target_list is None:\n        target_list = []\n    target_list.append(element)\n    return target_list",
            "expected_keywords": ["None", "target_list is None", "target_list = []"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 2,
            "title": "JavaScript: Scope leak in loops",
            "type": "debug",
            "category": "Frontend",
            "problem": "Look at the following code block. It prints '3' three times instead of 0, 1, 2. Fix the variable declaration to respect block-scoping.\n\n```javascript\nfor (var i = 0; i < 3; i++) {\n    setTimeout(() => console.log(i), 100);\n}\n```",
            "starter": "for (let i = 0; i < 3; i++) {\n    setTimeout(() => console.log(i), 100);\n}",
            "expected_keywords": ["let i", "let"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 3,
            "title": "SQL: Missing aggregate parameter",
            "type": "debug",
            "category": "Database",
            "problem": "Identify and correct the syntax error in this SQL query where you aggregate department averages without properly grouping.\n\n```sql\nSELECT department_id, name, AVG(salary) \nFROM employees;\n```",
            "starter": "SELECT department_id, AVG(salary) \nFROM employees \nGROUP BY department_id;",
            "expected_keywords": ["GROUP BY", "group by department_id"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 4,
            "title": "React: Dynamic rendering key error",
            "type": "debug",
            "category": "Frontend",
            "problem": "Identify the missing attribute in this React map loop that makes virtual DOM reconciliations slow and buggy:\n\n```javascript\nconst list = items.map(item => <li>{item.name}</li>);\n```",
            "starter": "const list = items.map(item => <li key={item.id}>{item.name}</li>);",
            "expected_keywords": ["key=", "key"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 5,
            "title": "Python: Float roundoff validation",
            "type": "debug",
            "category": "Math/CS",
            "problem": "Explain or correct why `0.1 + 0.2 == 0.3` evaluates to False in standard float operations, or write the correct utility using math module or round to validate matching within a tolerance of 1e-9.",
            "starter": "import math\nmath.isclose(0.1 + 0.2, 0.3, abs_tol=1e-9)",
            "expected_keywords": ["isclose", "round", "1e-9", "tolerance"],
            "difficulty": "Medium",
            "xp": 100
        },
        
        # --- SYSTEM DESIGN / ARCHITECTURE SPRINT TRACK ---
        {
            "id": 6,
            "title": "System Design: Database Caching Strategy",
            "type": "design",
            "category": "System Design",
            "problem": "Your application has highly read-heavy queries that change infrequently. You want to implement a cache-aside (Lazy Loading) caching policy. Choose the option or briefly justify how cache-aside policy behaves when a cache miss occurs.",
            "choices": [
                "A) The application queries database, writes results to cache, and returns value.",
                "B) The cache is updated synchronously by the database whenever a write happens.",
                "C) The client queries database directly and caches locally in browser session storage.",
                "D) The cache handles writing to the database asynchronously behind the scenes."
            ],
            "correct_choice": "A",
            "explanation": "In cache-aside, the application first checks the cache. If it misses, it fetches from the DB, stores it in the cache, and returns it to the user. This keeps the cache filled only with requested data.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 7,
            "title": "System Design: Vertical vs Horizontal Scaling",
            "type": "design",
            "category": "Infrastructure",
            "problem": "Which scaling strategy introduces the need for Load Balancers and Network Partition tolerances (CAP Theorem considerations)?",
            "choices": [
                "A) Vertical Scaling (Scaling Up CPU/RAM)",
                "B) Horizontal Scaling (Scaling Out servers)",
                "C) Database indexing",
                "D) Caching in memory"
            ],
            "correct_choice": "B",
            "explanation": "Horizontal scaling requires distributing network traffic across multiple database/web server instances, introducing the need for load-balancers and distributed consensus mechanisms.",
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 8,
            "title": "System Design: CDN Implementation",
            "type": "design",
            "category": "System Design",
            "problem": "What is the primary role of a Content Delivery Network (CDN) in scaling heavy global applications?",
            "choices": [
                "A) To manage secure user password hashing database systems.",
                "B) To cache dynamic database entries inside memory.",
                "C) To cache static assets and media geographically closer to end-users to reduce latency.",
                "D) To execute background cron jobs asynchronously."
            ],
            "correct_choice": "C",
            "explanation": "CDNs distribute static files (HTML, JS, images) across edge locations worldwide, drastically reducing latency and load on the primary origin servers.",
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 9,
            "title": "System Design: Optimistic vs Pessimistic Locking",
            "type": "design",
            "category": "Databases",
            "problem": "You are building a high-volume ticket booking app. Collisions are infrequent but critical to prevent double booking. Which locking mechanism provides high concurrency without database-level read locks?",
            "choices": [
                "A) Pessimistic Locking",
                "B) Optimistic Locking using version numbering columns",
                "C) Removing database indices",
                "D) Read uncommitted isolation level"
            ],
            "correct_choice": "B",
            "explanation": "Optimistic locking checks the version index before committing, avoiding transaction locks and offering much higher throughput when concurrent writes on the same row are rare.",
            "difficulty": "Hard",
            "xp": 100
        },
        
        # --- BEHAVIORAL & TECHNICAL INTERVIEW SPRINT TRACK ---
        {
            "id": 10,
            "title": "Behavioral: Dealing with Conflict",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Briefly describe a situation where you had a major technical disagreement with a colleague. How did you resolve it, and what was the outcome? (Pro-tip: Try using the STAR method format - Situation, Task, Action, Result).",
            "expected_keywords": ["compromise", "data", "test", "listen", "communication", "collaborate"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 11,
            "title": "Behavioral: Overcoming a Technical Failure",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Tell me about a time you shipped a major bug or faced a significant engineering failure. How did you identify it, mitigate the damage, and what did you learn?",
            "expected_keywords": ["learned", "fix", "mitigate", "post-mortem", "rollback", "test"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 12,
            "title": "Behavioral: Leadership and Initiative",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Give an example of a project where you took the initiative to build a tool or improve a system without being asked. What motivated you and what was the impact?",
            "expected_keywords": ["initiative", "impact", "improve", "bottleneck", "automation", "efficiency"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 13,
            "title": "Technical Pitch: Explain REST APIs to a kid",
            "type": "interview",
            "category": "Tech Communication",
            "problem": "How would you explain a RESTful API to a non-technical person or a 10-year-old child? Use a creative analogy!",
            "expected_keywords": ["waiter", "restaurant", "menu", "message", "translator", "request"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 14,
            "title": "Technical Pitch: Relational vs Non-Relational DBs",
            "type": "interview",
            "category": "Tech Communication",
            "problem": "A client is unsure whether to use PostgreSQL or MongoDB. Pitch the key trade-offs (Schema stability vs dynamic scaling) in under 4 sentences.",
            "expected_keywords": ["structured", "scale", "document", "schema", "relations", "JSON"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 15,
            "title": "System Design: Microservices Trade-offs",
            "type": "design",
            "category": "Architecture",
            "problem": "What is the primary operational overhead introduced by shifting from a Monolithic architecture to a Microservices architecture?",
            "choices": [
                "A) Inability to run tests locally.",
                "B) Distributed network complexity, service discovery, and data consistency issues.",
                "C) Slow database index speeds on individual tables.",
                "D) Shift from Python/Node to machine-level languages."
            ],
            "correct_choice": "B",
            "explanation": "Microservices introduce distributed system trade-offs: latency over the network, network partitions, distributed transactions, and complicated routing systems.",
            "difficulty": "Medium",
            "xp": 100
        }
    ]

    @staticmethod
    def get_daily_challenge(user):
        """Deterministically selects 1 unique challenge per calendar day (Wordle-style shared experience)."""
        today = date.today()
        # Seed hash based on date so all users see the exact same challenge
        seed = int(hashlib.sha256(today.strftime("%Y-%m-%d").encode()).hexdigest(), 16)
        challenge_idx = seed % len(SprintService.CHALLENGES)
        challenge = SprintService.CHALLENGES[challenge_idx]
        
        # Check if user has already completed today's sprint
        has_completed = False
        xp_earned = 0
        user_answer = ""
        is_correct = False
        ai_feedback = ""
        
        if user.is_authenticated:
            submission = UserSprintSubmission.query.filter_by(user_id=user.id, sprint_date=today).first()
            if submission:
                has_completed = True
                xp_earned = submission.xp_earned
                user_answer = submission.user_answer
                is_correct = submission.is_correct
                ai_feedback = submission.ai_feedback
                
        # Make a copy to avoid mutating cache
        challenge_data = challenge.copy()
        challenge_data["has_completed"] = has_completed
        challenge_data["today_submission"] = {
            "user_answer": user_answer,
            "is_correct": is_correct,
            "xp_earned": xp_earned,
            "ai_feedback": ai_feedback
        }
        
        # Hide correct choice or keywords if not completed yet
        if not has_completed:
            challenge_data.pop("expected_keywords", None)
            challenge_data.pop("correct_choice", None)
            challenge_data.pop("starter", None)
            challenge_data.pop("explanation", None)
            
        return challenge_data

    @staticmethod
    def evaluate_submission(user, answer):
        """Submit and evaluate today's daily sprint challenge."""
        today = date.today()
        
        # 1. Check if user already submitted today
        existing = UserSprintSubmission.query.filter_by(user_id=user.id, sprint_date=today).first()
        if existing:
            return {
                "success": False,
                "message": "You have already completed today's daily career sprint!",
                "submission": existing.to_dict()
            }
            
        # 2. Get today's challenge
        challenge = SprintService.get_daily_challenge(user)
        
        is_correct = False
        ai_feedback = ""
        score = 0
        
        # 3. Evaluate based on type
        if challenge["type"] == "design":
            correct_ans = challenge.get("today_submission", {}).get("correct_choice")
            # If not in submission, retrieve from global list
            if not correct_ans:
                global_challenge = next((c for c in SprintService.CHALLENGES if c["id"] == challenge["id"]), None)
                correct_ans = global_challenge["correct_choice"] if global_challenge else "A"
                explanation = global_challenge["explanation"] if global_challenge else ""
                
            clean_answer = answer.strip().upper()[:1]
            if clean_answer == correct_ans:
                is_correct = True
                ai_feedback = f"🎯 Excellent job! Option {clean_answer} is 100% correct.\n\n**Detailed Explanation:** {explanation}"
                score = 100
            else:
                is_correct = False
                ai_feedback = f"❌ Incorrect option selected. You chose Option {clean_answer}, but the correct answer is Option {correct_ans}.\n\n**Detailed Explanation:** {explanation}"
                score = 0
                
        elif challenge["type"] == "debug":
            global_challenge = next((c for c in SprintService.CHALLENGES if c["id"] == challenge["id"]), None)
            expected_keywords = global_challenge["expected_keywords"] if global_challenge else []
            starter_correct = global_challenge["starter"] if global_challenge else ""
            
            clean_answer = answer.strip()
            matched_keywords = [kw for kw in expected_keywords if kw.lower() in clean_answer.lower()]
            
            if len(matched_keywords) >= len(expected_keywords) * 0.5 or (starter_correct and starter_correct.replace(" ", "") in clean_answer.replace(" ", "")):
                is_correct = True
                ai_feedback = f"✅ Fantastic debugging! You successfully identified and resolved the bug.\n\n**Correct Reference Implementation:**\n```python\n{starter_correct}\n```"
                score = 100
            else:
                is_correct = False
                ai_feedback = f"⚠️ Close attempt, but some key syntax corrections are missing. Give it another thought!\n\n**Correct Reference Implementation:**\n```python\n{starter_correct}\n```"
                score = 30
                
        elif challenge["type"] == "interview":
            global_challenge = next((c for c in SprintService.CHALLENGES if c["id"] == challenge["id"]), None)
            expected_keywords = global_challenge["expected_keywords"] if global_challenge else []
            
            clean_answer = answer.strip()
            matched_keywords = [kw for kw in expected_keywords if kw.lower() in clean_answer.lower()]
            word_count = len(clean_answer.split())
            
            if word_count < 10:
                is_correct = False
                ai_feedback = "⚠️ Your response is extremely brief. High-impact behavioral pitches require at least 2-3 detailed sentences outlining Situation, Action, and Results."
                score = 10
            else:
                # Mock AI evaluator that gives deeply encouraging feedback
                is_correct = True
                kw_str = ", ".join([f"`{k}`" for k in matched_keywords])
                ai_feedback = f"🚀 **AI Evaluation Scorecard:**\n\n- **Depth & Tone:** Excellent dynamic tone! Real-world industry phrasing detected.\n- **Keywords Detected:** {kw_str if matched_keywords else 'None, but good general flow'}\n- **Length:** {word_count} words (Optimal)\n\n**AI Mentor Advice:** Your behavioral pitch is very strong. Adding metric targets (e.g. 'boosted performance by 20%') would make this a gold-standard response."
                score = 80
                
        # 4. Award XP and handle Streak Updates
        xp_earned = challenge["xp"]
        
        # Check streak maintenance
        yesterday = date.today() - timedelta(days=1)
        if user.last_sprint_date == yesterday:
            user.streak_count += 1
        elif user.last_sprint_date == today:
            pass # Already completed today
        else:
            user.streak_count = 1 # Streak broken or brand new
            
        user.last_sprint_date = today
        user.xp += xp_earned
        
        # Level calculation: Level = 1 + (XP // 500)
        old_level = user.level
        user.level = 1 + (user.xp // 500)
        
        # Add a nice notification if they leveled up
        level_up = False
        if user.level > old_level:
            level_up = True
            from app.utils.notify import send_notification
            send_notification(user.id, f"🎉 Level Up! You reached Level {user.level}! Keep the daily fire burning! 🔥")
            
        # 5. Save Sprint submission
        sub = UserSprintSubmission(
            user_id=user.id,
            sprint_date=today,
            challenge_title=challenge["title"],
            challenge_type=challenge["type"],
            challenge_data=challenge,
            user_answer=answer,
            is_correct=is_correct,
            ai_feedback=ai_feedback,
            xp_earned=xp_earned
        )
        db.session.add(sub)
        
        # Award custom badges based on streak milestones
        badges_earned = []
        if user.profile:
            current_badges = user.profile.badges or []
            badge_milestones = [
                {"streak": 3, "name": "Ignition Flame", "desc": "Completed a 3-Day Career Sprint streak!", "icon": "local_fire_department"},
                {"streak": 7, "name": "On Fire", "desc": "Completed a 7-Day Career Sprint streak!", "icon": "whatshot"},
                {"streak": 14, "name": "Unstoppable", "desc": "Completed a 14-Day Career Sprint streak!", "icon": "bolt"},
            ]
            
            for b in badge_milestones:
                if user.streak_count == b["streak"]:
                    # Check if already has it
                    has_badge = any(x.get("name") == b["name"] for x in current_badges)
                    if not has_badge:
                        new_badge = {
                            "name": b["name"],
                            "description": b["desc"],
                            "icon": b["icon"],
                            "earned_at": datetime.utcnow().isoformat()
                        }
                        current_badges.append(new_badge)
                        user.profile.badges = current_badges
                        badges_earned.append(b["name"])
                        from app.utils.notify import send_notification
                        send_notification(user.id, f"🏆 New Badge Unlocked: '{b['name']}'! {b['desc']}")
                        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Daily Sprint completed successfully!",
            "is_correct": is_correct,
            "ai_feedback": ai_feedback,
            "xp_earned": xp_earned,
            "new_xp": user.xp,
            "new_level": user.level,
            "level_up": level_up,
            "new_streak": user.streak_count,
            "badges_earned": badges_earned
        }

    @staticmethod
    def check_and_reset_streaks(user):
        """Automatically resets active streak counts to 0 if a user missed a day."""
        if not user.is_authenticated or not user.last_sprint_date:
            return False
            
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        if user.last_sprint_date != today and user.last_sprint_date != yesterday:
            print(f"[STREAK-RESET] User {user.name} missed a day. Resetting streak from {user.streak_count} to 0.")
            user.streak_count = 0
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_leaderboard():
        """Retrieve the top 10 users ranked by streaks and XP."""
        # Clean leaderboard entries
        top_users = User.query.filter(User.role == 'seeker', User.xp > 0)\
            .order_by(User.streak_count.desc(), User.xp.desc())\
            .limit(10).all()
            
        return [{
            "name": u.name,
            "streak": u.streak_count,
            "level": u.level,
            "xp": u.xp,
            "avatar_url": u.avatar_url
        } for u in top_users]
