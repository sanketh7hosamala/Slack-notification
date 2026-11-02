import json
import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from github import Auth, Github

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field('repo', description="Repository name in the format 'owner/repo'.")

class MyCustomTool(BaseTool):
    name: str = "MyCustomTool"
    description: str = (
        "This tool fetches issues from a GitHub repository. It takes a repository name in the format 'owner/repo' "
        "and returns a list of issues. The tool uses the GitHub API to fetch the issues."
        "Example: 'web2project/web2project' will return issues from the web2project repository."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return self.get_github_issues(argument)

    def get_github_issues(self, repo: str) -> str:
        """
        Fetches issues from a GitHub repository.
        
        Args:
            repo (str): The GitHub repository in the format 'owner/repo'.
        
        Returns:
            str: A string representation of the issues.
        """
        print(f"Fetching issues for repository: {repo}")
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {"state": "open", "per_page": 100}
        issues = []

        while url:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            page = response.json()
            if not isinstance(page, list):
                raise ValueError(f"GitHub returned an unexpected issues response for {repo}.")

            issues.extend(
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "html_url": issue["html_url"],
                    "body": issue.get("body") or "",
                    "state": issue["state"],
                    "labels": [label["name"] for label in issue.get("labels", [])],
                }
                for issue in page
                if "pull_request" not in issue
            )
            url = response.links.get("next", {}).get("url")
            params = None

        return json.dumps(issues, ensure_ascii=False)
    
    def update_github_issues(self, repo: str, issueId: int, labels: dict) -> str:
        """
        Updates issues in a GitHub repository.
        
        Args:
            repo (str): The GitHub repository in the format 'owner/repo'.
            labels (dict): 
        Returns:
            str: A string representation of the issues.
        """
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is not set.")
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo(repo)
        issue = repo.get_issue(number=issueId)
        issue.add_to_labels(labels)