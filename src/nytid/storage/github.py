from nytid.storage import git
import os
import re
import requests


class GitHubError(Exception):
    pass


def extract_github_repo_info(url: str) -> tuple:
    """
    Extracts GitHub repository owner and name from URL.

    Examples:
      'git@github.com:user/repo.git' -> ('user', 'repo')
      'https://github.com/user/repo.git' -> ('user', 'repo')
      'https://github.enterprise.com/user/repo' -> ('user', 'repo')

    Returns:
      Tuple of (owner, repo_name)
    """
    # Remove .git suffix if present
    if url.endswith(".git"):
        url = url[:-4]

    # Extract owner/repo from different formats
    if ":" in url and "@" in url:
        # SSH format: git@github.com:owner/repo
        parts = url.split(":")[-1]
    else:
        # HTTPS format: https://github.com/owner/repo
        parts = "/".join(url.split("/")[-2:])

    # Split owner/repo
    components = parts.split("/")
    if len(components) >= 2:
        return (components[-2], components[-1])
    else:
        raise GitHubError(f"Cannot extract owner/repo from URL: {url}")


def extract_github_hostname(url: str) -> str:
    """
    Extracts hostname from GitHub URL.

    Examples:
      'git@github.enterprise.com:user/repo.git' -> 'github.enterprise.com'
      'https://github.enterprise.com/user/repo' -> 'github.enterprise.com'
    """
    if url.startswith("http"):
        # HTTPS format
        match = re.match(r"https?://([^/]+)", url)
        if match:
            return match.group(1)
    elif "@" in url:
        # SSH format
        match = re.match(r"git@([^:]+):", url)
        if match:
            return match.group(1)

    raise GitHubError(f"Cannot extract hostname from URL: {url}")


class StorageRoot(git.StorageRoot):
    """
    Manages a storage root in a GitHub repository with access control.
    """

    def __init__(self, url: str, token: str = None):
        """
        Uses GitHub repository at `url` as storage root.

        Args:
          url: GitHub repository URL (SSH or HTTPS format)
          token: GitHub personal access token for API access.
                 If not provided, uses GITHUB_TOKEN environment variable.
        """
        self.__token = token or os.environ.get("GITHUB_TOKEN")
        if not self.__token:
            raise GitHubError(
                "GitHub token required. Provide token parameter or set GITHUB_TOKEN "
                "environment variable."
            )

        owner, repo_name = extract_github_repo_info(url)
        self.__owner = owner
        self.__repo = repo_name
        if "github.com" in url:
            self.__api_base = "https://api.github.com"
        else:
            # Extract hostname for GitHub Enterprise
            hostname = extract_github_hostname(url)
            self.__api_base = f"https://{hostname}/api/v3"
        self.__headers = {
            "Authorization": f"token {self.__token}",
            "Accept": "application/vnd.github.v3+json",
        }
        super().__init__(url)

    def grant_access(self, user: str, permission: str = "push"):
        """
        Grants access to the GitHub repository for a user.

        Args:
          user: GitHub username
          permission: Permission level - 'pull' (read), 'push' (write), or 'admin'

        Raises:
          GitHubError: If the API request fails
        """
        valid_permissions = ["pull", "push", "admin"]
        if permission not in valid_permissions:
            raise GitHubError(
                f"Invalid permission '{permission}'. "
                f"Must be one of: {', '.join(valid_permissions)}"
            )
        url = (
            f"{self.__api_base}/repos/{self.__owner}/{self.__repo}/"
            f"collaborators/{user}"
        )
        data = {"permission": permission}

        try:
            response = requests.put(url, headers=self.__headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise GitHubError(f"Failed to grant access to user '{user}': {err}")

    def revoke_access(self, user: str):
        """
        Revokes access to the GitHub repository for a user.

        Args:
          user: GitHub username

        Raises:
          GitHubError: If the API request fails
        """
        url = (
            f"{self.__api_base}/repos/{self.__owner}/{self.__repo}/"
            f"collaborators/{user}"
        )

        try:
            response = requests.delete(url, headers=self.__headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise GitHubError(f"Failed to revoke access for user '{user}': {err}")
