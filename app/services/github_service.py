import requests
from flask import current_app

class GitHubService:
    @staticmethod
    def get_user_data(github_url):
        """
        Fetches public data for a GitHub user.
        github_url: e.g., 'https://github.com/username'
        """
        if not github_url:
            return None
        
        username = github_url.strip('/').split('/')[-1]
        if not username:
            return None
            
        base_url = f"https://api.github.com/users/{username}"
        
        try:
            # Fetch user info
            user_response = requests.get(base_url, timeout=10)
            if user_response.status_code != 200:
                return None
            
            user_data = user_response.json()
            
            # Fetch public repos
            repos_response = requests.get(f"{base_url}/repos?sort=updated&per_page=10", timeout=10)
            repos_data = []
            if repos_response.status_code == 200:
                repos = repos_response.json()
                for repo in repos:
                    if not repo['fork']:
                        repos_data.append({
                            "name": repo['name'],
                            "description": repo['description'],
                            "language": repo['language'],
                            "stars": repo['stargazers_count'],
                            "updated_at": repo['updated_at']
                        })
            
            return {
                "username": username,
                "name": user_data.get("name"),
                "bio": user_data.get("bio"),
                "public_repos": user_data.get("public_repos"),
                "followers": user_data.get("followers"),
                "top_repos": repos_data
            }
        except Exception as e:
            current_app.logger.error(f"Error fetching GitHub data: {e}")
            return None
