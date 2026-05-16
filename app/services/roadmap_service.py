from app.models.roadmap import Roadmap
from app.extensions import db

class RoadmapService:
    ROLE_ROADMAPS = {
        "Senior AI Engineer": [
            {"title": "Master Advanced Python", "description": "Deep dive into concurrency, decorators, and meta-programming.", "resources": ["Fluent Python Book", "PyCon Talks"]},
            {"title": "Deep Learning Specialization", "description": "Master Transformers, CNNs, and RNNs.", "resources": ["Coursera", "Fast.ai"]},
            {"title": "MLOps & Scalability", "description": "Learn Kubernetes, Kubeflow, and Model Monitoring.", "resources": ["AWS SageMaker Docs", "Docker Mastery"]},
            {"title": "System Design for AI", "description": "Design distributed training systems and low-latency inference.", "resources": ["Grokking System Design"]}
        ],
        "Full Stack Developer": [
            {"title": "Advanced Frontend", "description": "Master React Patterns, Redux, and Next.js.", "resources": ["Frontend Masters", "Next.js Docs"]},
            {"title": "Backend Scalability", "description": "Microservices with Python/Flask and gRPC.", "resources": ["Real Python", "Microservices Patterns"]},
            {"title": "Cloud Infrastructure", "description": "Deploying with AWS and Terraform.", "resources": ["Terraform Up & Running"]},
            {"title": "Database Optimization", "description": "Advanced PostgreSQL and Redis caching.", "resources": ["High Performance Browser Networking"]}
        ]
    }

    @staticmethod
    def generate_roadmap(user_id, target_role):
        # Fetch template or use default
        steps_template = RoadmapService.ROLE_ROADMAPS.get(target_role, [
            {"title": "Core Foundations", "description": "Master the basics of your chosen field.", "resources": []},
            {"title": "Advanced Techniques", "description": "Specialize in modern frameworks.", "resources": []},
            {"title": "Portfolio Building", "description": "Build 3 high-impact projects.", "resources": []},
            {"title": "Interview Prep", "description": "Focus on data structures and behavioral questions.", "resources": []}
        ])

        # Add status to steps
        steps = []
        for step in steps_template:
            steps.append({**step, "status": "todo"})

        roadmap = Roadmap(
            user_id=user_id,
            target_role=target_role,
            steps=steps
        )
        db.session.add(roadmap)
        db.session.commit()
        return roadmap

    @staticmethod
    def update_step_status(roadmap_id, step_index, status):
        roadmap = Roadmap.query.get(roadmap_id)
        if roadmap:
            steps = list(roadmap.steps)
            if 0 <= step_index < len(steps):
                steps[step_index]['status'] = status
                roadmap.steps = steps
                db.session.commit()
        return roadmap
