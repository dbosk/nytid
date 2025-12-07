from nytid import storage
import pathlib
import subprocess
import sys
import tempfile


class GitError(Exception):
    pass


def extract_repo_name(url: str) -> str:
    """
    Extracts repository name from Git URL.
    Examples:
      'git@github.com:user/repo.git' -> 'user_repo'
      'https://github.com/user/repo.git' -> 'user_repo'
    """
    # Remove .git suffix if present
    if url.endswith(".git"):
        url = url[:-4]

    # Extract last two path components (user/repo)
    if ":" in url and "@" in url:
        # SSH format: git@github.com:user/repo
        parts = url.split(":")[-1].split("/")
    elif url.startswith("http"):
        # HTTPS format: https://github.com/user/repo
        parts = url.split("/")
    else:
        # Local path format
        parts = url.split("/")

    # Take last two non-empty parts and join with underscore
    non_empty = [p for p in parts if p]
    if len(non_empty) >= 2:
        return f"{non_empty[-2]}_{non_empty[-1]}"
    elif len(non_empty) == 1:
        return non_empty[-1]
    else:
        return "repo"


def get_local_repo_path(repo_name: str) -> pathlib.Path:
    """
    Returns path where Git repository should be cloned locally.
    Uses XDG cache directory structure.
    """
    cache_dir = pathlib.Path.home() / ".cache" / "nytid" / "git-repos"
    return cache_dir / repo_name


def run_git_command(args, cwd=None):
    """
    Runs a Git command with the given arguments.

    Args:
      args: List of command arguments (e.g., ['clone', 'url', 'path'])
      cwd: Working directory for the command

    Raises:
      GitError: If the command fails
    """
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as err:
        raise GitError(f"Git command failed: {' '.join(cmd)}\n" f"Error: {err.stderr}")
    except FileNotFoundError:
        raise GitError("Git is not installed or not in PATH")


class StorageRoot(storage.StorageRoot):
    """
    Manages a storage root in a Git repository.
    """

    def __init__(self, url: str):
        """
        Uses Git repository at `url` as storage root.
        Clones the repository if needed, or uses existing clone.
        For local paths, uses the repository directly if it exists.
        """
        self.__url = url
        self.__repo_name = self.__extract_repo_name(url)
        self.__repo_path = self.__get_local_repo_path(self.__repo_name)
        local_path = pathlib.Path(self.__url)
        self.__is_local = local_path.exists() and local_path.is_dir()
        if self.__is_local:
            # Use the local path directly, don't use cache
            self.__repo_path = local_path
        else:
            # Remote URL - will clone to cache
            pass
        if not self.__is_local:
            if not self.__repo_path.exists():
                try:
                    run_git_command(["clone", self.__url, str(self.__repo_path)])
                except GitError as err:
                    raise GitError(f"Failed to clone repository {self.__url}: {err}")
            else:
                try:
                    run_git_command(["status"], cwd=self.__repo_path)
                except GitError as err:
                    raise GitError(
                        f"Directory {self.__repo_path} exists but is not a valid Git repository"
                    )
            try:
                run_git_command(["pull"], cwd=self.__repo_path)
            except GitError as err:
                # Pull failure is not fatal - we can work with local changes
                pass
        super().__init__(self.__repo_path)

    def __extract_repo_name(self, url: str) -> str:
        """Extracts repository name from URL"""
        return extract_repo_name(url)

    def __get_local_repo_path(self, repo_name: str) -> pathlib.Path:
        """Returns local path for repository"""
        return get_local_repo_path(repo_name)

    def commit_changes(self, message: str = "Update from nytid"):
        """
        Commits and pushes all changes in the repository.
        For local repositories without remotes, only commits locally.

        Args:
          message: Commit message
        """
        try:
            # Stage all changes
            run_git_command(["add", "-A"], cwd=self.__repo_path)

            # Check if there are changes to commit
            try:
                run_git_command(["diff", "--cached", "--quiet"], cwd=self.__repo_path)
                # No changes to commit
                return
            except GitError:
                # Changes exist, proceed with commit
                pass

            # Commit changes
            run_git_command(["commit", "-m", message], cwd=self.__repo_path)

            # Try to push changes if there's a remote configured
            try:
                run_git_command(["push"], cwd=self.__repo_path)
            except GitError:
                # No remote configured or push failed - that's OK for local repos
                pass
        except GitError as err:
            raise GitError(f"Failed to commit changes: {err}")

    def pull_changes(self):
        """
        Pulls the latest changes from the remote repository.
        """
        try:
            run_git_command(["pull"], cwd=self.__repo_path)
        except GitError as err:
            raise GitError(f"Failed to pull changes: {err}")

    def grant_access(self, user):
        """
        Access control is not available for basic Git storage.
        Use the GitHub storage backend for access control.
        """
        raise NotImplementedError(
            "Access control requires a Git hosting platform. "
            "Use nytid.storage.github for GitHub repositories."
        )

    def revoke_access(self, user):
        """
        Access control is not available for basic Git storage.
        Use the GitHub storage backend for access control.
        """
        raise NotImplementedError(
            "Access control requires a Git hosting platform. "
            "Use nytid.storage.github for GitHub repositories."
        )
