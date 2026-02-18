import os
import time
import re
from typing import List, Dict, Optional, Any
from github import Github, GithubException
from dotenv import load_dotenv

from src.logger import logging
from src.exceptions import CustomException
from src.utils.github_utils import clean_github_url, is_valid_github_url, extract_repo_info
from src.entity.config import GitHubFetcherConfig,ConfigEntity

from src.entity.artifacts import DataReaderArtifact,GitHubFetcherArtifact

load_dotenv()

class GitHubFetcher:
    def __init__(self, keywords: List[str] = None):
        """
        Initializes the GitHub API client and search criteria.
        
        Args:
            keywords: List of strings to look for in repo names/descriptions (e.g., ['pandas', 'assignment'])
        """
        self.keywords = keywords or []
        self.github_fetcher_config = GitHubFetcherConfig(config=ConfigEntity())
        
        if not self.github_fetcher_config.github_token:
            logging.error("GITHUB_TOKEN not found in environment variables.")
            raise ValueError("GITHUB_TOKEN is required for GitHubFetcher.")
            
        self.g = Github(self.github_fetcher_config.github_token)
        logging.info(f"GitHubFetcher initialized with keywords: {self.keywords}")

        logging.info(f"Rate Limit: {self.g.get_rate_limit().rate.limit}")

    def _check_rate_limit(self):
        """Monitors API usage and pauses if limits are nearly exhausted."""
        rate_limit = self.g.get_rate_limit()
        remaining = rate_limit.rate.remaining
        reset_time = rate_limit.rate.reset
        
        if remaining < 20:  # Safety buffer
            wait_time = max((reset_time - time.time()) + 5, 0)
            logging.warning(f"Rate limit low ({remaining} left). Sleeping for {wait_time:.0f}s")
            time.sleep(wait_time)

    def _get_latest_repo(self, username: str):
        """Finds the most recent repo, prioritizing keyword matches."""
        self._check_rate_limit()
        try:
            user = self.g.get_user(username)
            # Use 'pushed' instead of 'created' to get the most recently active repo
            repos = user.get_repos(sort="pushed", direction="desc")
            
            all_repos = list(repos)
            if not all_repos:
                return None

            # 1. Try to find a match with keywords
            if self.keywords:
                for repo in all_repos:
                    repo_text = f"{repo.name} {repo.description or ''}".lower()
                    if any(k.lower() in repo_text for k in self.keywords):
                        logging.info(f"Found keyword match: {repo.full_name}")
                        return repo
            
            # 2. Fallback: Return the most recently pushed non-forked repo 
            # if no keyword match or no keywords provided
            for repo in all_repos:
                if not repo.fork:
                    logging.info(f"No keyword match. Falling back to latest active repo: {repo.full_name}")
                    return repo
                    
            return all_repos[0] # Ultimate fallback
            
        except GithubException as e:
            logging.error(f"GitHub API error for user {username}: {e}")
            return None

    def _find_notebook_in_repo(self, repo, path="", depth=0, max_depth=2):
        """
        Improved search: Looks for non-empty notebooks and prioritizes 
        files matching keywords.
        """
        if depth > max_depth:
            return None
            
        self._check_rate_limit()
        try:
            contents = repo.get_contents(path)
            notebooks = []
            directories = []

            for item in contents:
                if item.type == "file" and item.name.lower().endswith(".ipynb"):
                    # Check if file is non-empty before adding to candidates
                    if item.size > 0: 
                        notebooks.append(item)
                elif item.type == "dir" and depth < max_depth:
                    if item.name.lower() in ["", "notebooks", "src", "code", "project", "assignments"]:
                        directories.append(item)

            # 1. Best Case: Found notebooks in current directory
            if notebooks:
                # Sort notebooks: prioritize ones with keywords in filename
                for nb in notebooks:
                    if any(k.lower() in nb.name.lower() for k in self.keywords):
                        return nb
                # Fallback to the first non-empty notebook found
                return notebooks[0]

            # 2. Recurse into directories if no notebook found here
            for folder in directories:
                result = self._find_notebook_in_repo(repo, folder.path, depth + 1, max_depth)
                if result:
                    return result
                    
            return None
        except Exception as e:
            logging.debug(f"Search failed in {path}: {e}")
            return None

    def fetch_single_student_data(self, student_name: str, raw_url: str) -> Optional[Dict]:
        try:
            # 1. Clean and Parse URL
            clean_url = clean_github_url(raw_url)
            if not is_valid_github_url(clean_url):
                logging.warning(f"Skipping invalid URL for {student_name}: {raw_url}")
                return None
            
            username, repo_name = extract_repo_info(clean_url)
            repo = None

            # 2. Strategy A: Direct Repo Access (The Target Link)
            if username and repo_name:
                try:
                    full_path = f"{username}/{repo_name}"
                    self._check_rate_limit()
                    repo = self.g.get_repo(full_path)
                    logging.info(f"Directly accessed repo: {full_path}")
                except GithubException:
                    logging.warning(f"Could not find specific repo {username}/{repo_name}. Trying search...")

            # 3. Strategy B: Fallback to Keyword Search (If Strategy A failed or no repo in URL)
            if not repo and username:
                repo = self._get_latest_repo(username)

            if not repo:
                logging.warning(f"No usable repository found for student: {student_name}")
                return None
            
            # 4. Find and Validate Notebook in the identified Repo
            notebook = self._find_notebook_in_repo(repo)
            if not notebook:
                logging.warning(f"No .ipynb file found in {repo.full_name}")
                return None

            try:
                content_bytes = notebook.decoded_content
                if not content_bytes or len(content_bytes.strip()) == 0:
                    logging.warning(f"Notebook '{notebook.name}' is empty for {student_name}.")
                    return None
            except Exception as e:
                logging.error(f"Failed to decode content for {student_name}: {e}")
                return None

            return {
                "student_name": student_name,
                "github_link": raw_url,  # <--- ADD THIS LINE
                "github_username": username,
                "repo_name": repo.name,
                "notebook_name": notebook.name,
                "notebook_path": notebook.path,
                "download_url": notebook.download_url,
                "raw_content": content_bytes
            }

        except Exception as e:
            logging.error(f"Error processing {student_name}: {e}")
            return None

    def process_all_students(self, artifact: DataReaderArtifact) -> List[Dict[str, Any]]:
        """
        Updated to handle DataReaderArtifact instead of a raw list.
        """
        # Access the dictionary/list inside the artifact
        students_list = artifact.student_records
        
        logging.info(f"Starting GitHub fetch for {len(students_list)} students...")
        final_results = []
        
        for student in students_list:
            data = self.fetch_single_student_data(
                student.get('student_name'), 
                student.get('github_link')
            )
            if data:
                final_results.append(data)
                
        logging.info(f"Successfully retrieved {len(final_results)} student notebooks.")

        artifact = GitHubFetcherArtifact(notebook_data=final_results)
        return artifact