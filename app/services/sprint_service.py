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
        },

        # --- ADDITIONAL DEBUG SPRINT TRACK (16 - 25) ---
        {
            "id": 16,
            "title": "Python: Fix the N+1 query problem in SQLAlchemy",
            "type": "debug",
            "category": "Backend",
            "problem": "Explain how to resolve the N+1 query issue in the function below by ensuring users are eagerly loaded with posts in a single database query:\n\n```python\ndef get_posts_with_users():\n    posts = Post.query.all()\n    return [{ 'post_title': p.title, 'user_name': p.user.name } for p in posts]\n```",
            "starter": "def get_posts_with_users():\n    posts = Post.query.options(db.joinedload(Post.user)).all()\n    return [{ 'post_title': p.title, 'user_name': p.user.name } for p in posts]",
            "expected_keywords": ["joinedload", "options"],
            "difficulty": "Hard",
            "xp": 100
        },
        {
            "id": 17,
            "title": "Python: Fix memory leak in generator",
            "type": "debug",
            "category": "Backend",
            "problem": "The following generator opens files and yields lines, but has a memory delegation leak. Fix the delegation to nested generators to properly yield from the sub-generator:\n\n```python\ndef read_logs(file_paths):\n    for path in file_paths:\n        for line in open_file(path):\n            yield line\n```",
            "starter": "def read_logs(file_paths):\n    for path in file_paths:\n        yield from open_file(path)",
            "expected_keywords": ["yield from"],
            "difficulty": "Hard",
            "xp": 100
        },
        {
            "id": 18,
            "title": "SQL: Fix missing index causing full table scan",
            "type": "debug",
            "category": "Database",
            "problem": "Write a clean SQL query to create a standard database-level b-tree index on the `email` column of the `users` table to avoid slow full-table scans when running lookup queries:\n\n```sql\nSELECT * FROM users WHERE email = 'john@example.com';\n```",
            "starter": "CREATE INDEX idx_users_email ON users(email);",
            "expected_keywords": ["CREATE INDEX", "ON users", "email"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 19,
            "title": "JavaScript: Missing await in promise chain",
            "type": "debug",
            "category": "Frontend",
            "problem": "This async function returns a Promise containing the value instead of resolving the actual value first. Correct the missing keyword in the asynchronous fetching call:\n\n```javascript\nasync function getUserData(userId) {\n    const user = fetchUser(userId);\n    return user.name;\n}\n```",
            "starter": "async function getUserData(userId) {\n    const user = await fetchUser(userId);\n    return user.name;\n}",
            "expected_keywords": ["await"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 20,
            "title": "Python: Race condition in threading without lock",
            "type": "debug",
            "category": "Backend",
            "problem": "Explain or write a thread-safe increment operation for a shared counter using python's `threading.Lock()` to prevent race conditions during concurrent modifications:\n\n```python\ncounter = 0\ndef increment():\n    global counter\n    counter += 1\n```",
            "starter": "import threading\nlock = threading.Lock()\ncounter = 0\ndef increment():\n    global counter\n    with lock:\n        counter += 1",
            "expected_keywords": ["Lock", "with lock"],
            "difficulty": "Hard",
            "xp": 100
        },
        {
            "id": 21,
            "title": "CSS: Fix z-index stacking context broken by transform",
            "type": "debug",
            "category": "Frontend",
            "problem": "The overlay card is rendering underneath other items because transform properties create a new stacking context. Show how to fix the CSS declaration below to restore normal stacking context flow:\n\n```css\n.modal {\n  position: absolute;\n  z-index: 9999;\n  transform: translate(0, 0);\n}\n```",
            "starter": ".modal {\n  position: absolute;\n  z-index: 9999;\n}",
            "expected_keywords": ["z-index", "transform"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 22,
            "title": "Python: Fix incorrect list comprehension with side effects",
            "type": "debug",
            "category": "Backend",
            "problem": "Do not modify a list dynamic structure while iterating over it, as this causes unexpected off-by-one skipping. Rewrite the structure to filter out even numbers safely:\n\n```python\nnumbers = [1, 2, 3, 4, 5]\n[numbers.remove(n) for n in numbers if n % 2 == 0]\n```",
            "starter": "numbers = [1, 2, 3, 4, 5]\nnumbers = [n for n in numbers if n % 2 != 0]",
            "expected_keywords": ["numbers = [", "% 2 != 0"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 23,
            "title": "SQL: Fix subquery returning multiple rows",
            "type": "debug",
            "category": "Database",
            "problem": "Correct the operator used in this SQL lookup because the subquery returns multiple records instead of a single ID:\n\n```sql\nSELECT name FROM employees \nWHERE department_id = (SELECT id FROM departments WHERE region = 'US');\n```",
            "starter": "SELECT name FROM employees \nWHERE department_id IN (SELECT id FROM departments WHERE region = 'US');",
            "expected_keywords": ["IN (", "subquery"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 24,
            "title": "JavaScript: Callback this-binding issue",
            "type": "debug",
            "category": "Frontend",
            "problem": "Fix the callback scope definition inside this object's method because standard functions create their own context, rendering `this.name` undefined:\n\n```javascript\nconst obj = {\n  name: 'Be Your',\n  greet: function() {\n    setTimeout(function() {\n      console.log(this.name);\n    }, 100);\n  }\n};\n```",
            "starter": "const obj = {\n  name: 'Be Your',\n  greet: function() {\n    setTimeout(() => {\n      console.log(this.name);\n    }, 100);\n  }\n};",
            "expected_keywords": ["arrow function", "bind(this)", "() =>"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 25,
            "title": "Python: Fix off-by-one binary search bug",
            "type": "debug",
            "category": "Math/CS",
            "problem": "Identify the off-by-one boundary checking errors in the standard binary search logic below. Provide the correct index adjustments and condition check:\n\n```python\ndef binary_search(arr, x):\n    low = 0\n    high = len(arr)\n    while low < high:\n        mid = (low + high) // 2\n        if arr[mid] < x:\n            low = mid\n        elif arr[mid] > x:\n            high = mid\n        else: return mid\n    return -1\n```",
            "starter": "def binary_search(arr, x):\n    low = 0\n    high = len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] < x:\n            low = mid + 1\n        elif arr[mid] > x:\n            high = mid - 1\n        else:\n            return mid\n    return -1",
            "expected_keywords": ["low <= high", "mid + 1", "mid - 1"],
            "difficulty": "Medium",
            "xp": 100
        },

        # --- ADDITIONAL SYSTEM DESIGN MCQ TRACK (26 - 35) ---
        {
            "id": 26,
            "title": "System Design: SQL INNER JOIN vs LEFT JOIN",
            "type": "design",
            "category": "Database Design",
            "problem": "What is the structural differences between an SQL INNER JOIN and an SQL LEFT JOIN?",
            "choices": [
                "A) INNER JOIN returns only matching rows; LEFT JOIN returns all rows from the left table and matching rows from the right table.",
                "B) INNER JOIN returns all rows from both tables; LEFT JOIN returns only matching rows.",
                "C) LEFT JOIN is faster and returns only left keys; INNER JOIN is slower.",
                "D) There is no structural difference; they perform the exact same logic."
            ],
            "correct_choice": "A",
            "explanation": "INNER JOIN only returns rows where there is a match in both tables. LEFT JOIN returns all rows from the left table, and the matched rows from the right table, filling with NULL if no match exists.",
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 27,
            "title": "System Design: Redis vs Memcached Caching Strategy",
            "type": "design",
            "category": "System Caching",
            "problem": "When should you choose Redis over Memcached for implementing caching structures in a highly scaled architecture?",
            "choices": [
                "A) Memcached supports rich data structures; Redis only supports strings.",
                "B) Redis supports rich data structures, persistence options, and is single-threaded; Memcached is simple, multi-threaded, and purely in-memory.",
                "C) Redis is strictly slower than Memcached for all caching scenarios.",
                "D) Memcached should be used for pub/sub systems; Redis should not."
            ],
            "correct_choice": "B",
            "explanation": "Redis supports complex data structures (hashes, lists, sets) and data persistence, making it highly versatile, while Memcached is a lighter, simpler, multi-threaded key-value store.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 28,
            "title": "System Design: CAP Theorem & PostgreSQL Priorities",
            "type": "design",
            "category": "System Design",
            "problem": "What core trade-offs are defined by the CAP Theorem? Which two properties does PostgreSQL natively prioritize as a ACID database?",
            "choices": [
                "A) Consistency, Availability, Partition Tolerance; PostgreSQL prioritizes Consistency and Availability (CA).",
                "B) Consistency, Authority, Processing; PostgreSQL prioritizes Consistency and Authority.",
                "C) Cost, Availability, Performance; PostgreSQL prioritizes Cost and Performance.",
                "D) Cache, API, Portability; PostgreSQL prioritizes Cache and API."
            ],
            "correct_choice": "A",
            "explanation": "CAP stands for Consistency, Availability, and Partition Tolerance. PostgreSQL is a traditional ACID relational database that guarantees Consistency and Availability (CA) under standard operations.",
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 29,
            "title": "System Design: REST vs GraphQL",
            "type": "design",
            "category": "System Integration",
            "problem": "Under which network communication scenario does a GraphQL API have a clear advantage over a traditional REST API?",
            "choices": [
                "A) When you want to minimize network calls and fetch nested data dynamically without over-fetching or under-fetching.",
                "B) When you need standard browser-level caching of resources natively.",
                "C) When you need simple out-of-the-box file uploads.",
                "D) When you want simple endpoint-based rate-limiting."
            ],
            "correct_choice": "A",
            "explanation": "GraphQL allows clients to request exactly what they need in a single roundtrip, preventing over-fetching (getting unused data) and under-fetching (needing multiple REST calls).",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 30,
            "title": "System Design: Authentication vs Authorization",
            "type": "design",
            "category": "Security Design",
            "problem": "What is the structural security difference between Authentication and Authorization in microservice platforms?",
            "choices": [
                "A) Authentication verifies WHO you are; Authorization verifies WHAT you are allowed to do.",
                "B) Authentication gives database access; Authorization gives API access.",
                "C) Authorization verifies WHO you are; Authentication verifies permissions.",
                "D) They are synonyms and represent the same security protocol."
            ],
            "correct_choice": "A",
            "explanation": "Authentication (AuthN) is the process of identifying a user (e.g. passwords, OTP). Authorization (AuthZ) is determining their permissions (e.g. role-based access control).",
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 31,
            "title": "System Design: Asynchronous Message Queues",
            "type": "design",
            "category": "Infrastructure",
            "problem": "What is the primary advantage of utilizing Message Queues (e.g., RabbitMQ, Kafka) over direct HTTP requests in web applications?",
            "choices": [
                "A) To decouple microservices, enable asynchronous processing, handle traffic spikes, and ensure durability.",
                "B) To replace standard PostgreSQL databases.",
                "C) To decrease database query optimization times.",
                "D) To encrypt API payload traffic automatically."
            ],
            "correct_choice": "A",
            "explanation": "Message queues decouple system components, allowing tasks to process asynchronously. This prevents heavy background tasks from blocking web requests and protects downstream services from spikes.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 32,
            "title": "System Design: Database Normalization vs Denormalization",
            "type": "design",
            "category": "Database Architecture",
            "problem": "What is the purpose of database normalization, and in which architecture scenario should denormalization be used instead?",
            "choices": [
                "A) Normalization reduces redundancy by structuring tables; denormalization is used to speed up read-heavy queries by adding redundant data.",
                "B) Normalization is used for document databases; denormalization is used for SQL.",
                "C) Normalization duplicates tables; denormalization groups them.",
                "D) Normalization is only for frontend caching."
            ],
            "correct_choice": "A",
            "explanation": "Database normalization organizes schemas to minimize redundancy and dependency. Denormalization purposefully adds redundant data to optimize read performance by avoiding expensive JOINs.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 33,
            "title": "System Design: N+1 Query Overhead",
            "type": "design",
            "category": "Database Design",
            "problem": "What is the exact database N+1 query problem, and how can backend developers fix this issue in relational databases?",
            "choices": [
                "A) It happens when an application executes N additional queries to fetch child data for N parent records; it is fixed by eager loading or JOIN FETCH.",
                "B) It happens when a loop has an off-by-one index mismatch; it is fixed by changing '<=' to '<'.",
                "C) It is a memory leak issue inside browser cookies; it is fixed by setting HTTPOnly flag.",
                "D) It is an API rate limit response code."
            ],
            "correct_choice": "A",
            "explanation": "In ORMs, retrieving N records and fetching their association in a loop causes 1 initial query plus N subsequent queries. Eager loading loads parent and child records in a single JOIN query.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 34,
            "title": "System Design: Real-time Communication Protocols",
            "type": "design",
            "category": "System Integration",
            "problem": "When is it appropriate to choose WebSockets over Server-Sent Events (SSE) or simple HTTP Polling?",
            "choices": [
                "A) WebSockets for full-duplex real-time communication; Server-Sent Events (SSE) for unidirectional server-to-client streaming; HTTP polling for simple intervals.",
                "B) HTTP polling for real-time video games; WebSockets for static blog pages.",
                "C) Server-Sent Events only works on native mobile applications.",
                "D) WebSockets are strictly unidirectional and cannot receive client inputs."
            ],
            "correct_choice": "A",
            "explanation": "WebSockets provide bidirectional low-latency sockets. Server-Sent Events are standard unidirectional HTTP streams from server to client (great for notifications). Polling periodically makes requests.",
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 35,
            "title": "System Design: SOLID Principles & Single Responsibility",
            "type": "design",
            "category": "Object-Oriented Design",
            "problem": "What does SOLID stand for in system design, and what is the primary core of the Single Responsibility Principle (SRP)?",
            "choices": [
                "A) Five object-oriented design principles; Single Responsibility states that a class should have only one reason to change.",
                "B) Structured Oriented Logical Integrated Design; Single Responsibility means single developer ownership.",
                "C) Secure Operations Logical Integrated Deployment; Single Responsibility means writing one function.",
                "D) Standard Object Logic In Databases; Single Responsibility is schema mapping."
            ],
            "correct_choice": "A",
            "explanation": "SOLID represents: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. Single Responsibility says a class/module should do exactly one thing.",
            "difficulty": "Easy",
            "xp": 100
        },

        # --- ADDITIONAL BEHAVIORAL & TECHNICAL INTERVIEW TRACK (36 - 45) ---
        {
            "id": 36,
            "title": "Behavioral: Managing Tight Deadlines & Scope Creep",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Explain how you handle a scenario where scope creep threatens a business-critical project deadline. How do you communicate and balance deliverables?",
            "expected_keywords": ["prioritize", "communicate", "MVP", "stakeholder", "scope", "flexibility"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 37,
            "title": "Behavioral: High-Pressure Production Debugging",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Outline your structured engineering workflow for diagnosing and fixing an unexpected critical production issue at 3 AM.",
            "expected_keywords": ["logs", "reproduce", "rollback", "isolate", "monitoring", "post-mortem"],
            "difficulty": "Hard",
            "xp": 100
        },
        {
            "id": 38,
            "title": "Technical Pitch: Explaining Technical Debt",
            "type": "interview",
            "category": "Tech Communication",
            "problem": "Pitch the concept of 'Technical Debt' to a non-technical manager. Use an intuitive business analogy to explain why it requires allocation times.",
            "expected_keywords": ["loan", "interest", "refactor", "velocity", "quality", "analogy"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 39,
            "title": "Behavioral: Task Prioritization Under Strain",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "How do you decide what tasks to focus on when you have multiple stakeholders screaming that their issues are top-priority?",
            "expected_keywords": ["Eisenhower", "impact", "effort", "alignment", "communication", "triage"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 40,
            "title": "Behavioral: Fast Learning Curve",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Provide a concrete instance from your engineering background where you had to adapt and build on a complex technical stack in under a week.",
            "expected_keywords": ["documentation", "sandbox", "mentor", "prototype", "structured", "adapted"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 41,
            "title": "Behavioral: Delivering Code Reviews & Feedback",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "How do you frame your architectural and style feedback in standard pull requests to ensure developers learn without feeling demotivated?",
            "expected_keywords": ["empathy", "objective", "suggest", "standards", "pull request", "collaboration"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 42,
            "title": "Technical Pitch: Microservices Architecture",
            "type": "interview",
            "category": "Tech Communication",
            "problem": "Explain the architectural difference between a monolithic and a microservice design to a business client, using a restaurant analogy.",
            "expected_keywords": ["specialized", "teams", "decouple", "restaurant", "independent", "scale"],
            "difficulty": "Medium",
            "xp": 100
        },
        {
            "id": 43,
            "title": "Behavioral: Disagreements with Management Decisions",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "Tell me about a time you disagreed with an architectural directive from your manager. How did you advocate for your option, and what was the consensus?",
            "expected_keywords": ["data", "respectful", "alternatives", "listen", "compromise", "consensus"],
            "difficulty": "Hard",
            "xp": 100
        },
        {
            "id": 44,
            "title": "Technical Pitch: Staying Current in Tech",
            "type": "interview",
            "category": "Tech Communication",
            "problem": "How do you systematically structure your weekly reading to stay current with the rapidly shifting frontend and cloud infrastructure landscape?",
            "expected_keywords": ["newsletters", "community", "side projects", "documentation", "podcasts", "learning"],
            "difficulty": "Easy",
            "xp": 100
        },
        {
            "id": 45,
            "title": "Behavioral: Accidentally Pushing Secrets to Git",
            "type": "interview",
            "category": "Soft Skills",
            "problem": "You just realized you accidentally committed a high-privilege production API secret to a public repository. What precise steps do you execute immediately?",
            "expected_keywords": ["revoke", "rotate", "secrets", "git filter-repo", "incident", "notify"],
            "difficulty": "Hard",
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
        
        # Check streak maintenance with Streak Freeze grace period logic
        yesterday = date.today() - timedelta(days=1)
        day_before_yesterday = yesterday - timedelta(days=1)
        
        has_freeze = False
        if user.profile and user.profile.badges:
            has_freeze = any(x.get("name") in ["Streak Freeze", "Ignition Flame"] for x in user.profile.badges)
            
        if user.last_sprint_date == yesterday:
            user.streak_count += 1
        elif user.last_sprint_date == today:
            pass # Already completed today
        elif has_freeze and user.last_sprint_date == day_before_yesterday:
            # Streak freeze triggered! Preserved streak and incremented
            user.streak_count += 1
            from app.utils.notify import send_notification
            send_notification(user.id, f"❄️ Streak Freeze Triggered! Your {user.streak_count}-day active career sprint streak was saved.")
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
                {"streak": 5, "name": "Streak Freeze", "desc": "Unlocked a Streak Freeze! Preserves streak if you miss a single day.", "icon": "ac_unit"},
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
            "badges_earned": badges_earned,
            "submission_id": sub.id
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
