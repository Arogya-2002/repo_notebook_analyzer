import re

def clean_github_url(url):
    """
    Aggressively cleans strings from Excel/Google Sheets.
    Handles non-breaking spaces, standard spaces, and ensures 
    the string is a valid format for regex checking.
    """
    if not isinstance(url, str):
        return ""
    
    # 1. Remove all whitespace characters, including \xa0 (non-breaking space)
    # and \n, \t, etc.
    url = re.sub(r'\s+', '', url)
    
    # 2. Basic cleanup: remove trailing slashes and convert to lowercase 
    # for consistency (usernames/repos are case-insensitive in URLs)
    url = url.strip().rstrip('/')
    
    return url

def is_valid_github_url(url: str) -> bool:
    """
    Validates if a string is a legitimate GitHub profile or repository URL.
    Supports:
    - https://github.com/user
    - https://www.github.com/user/repo
    - github.com/user (missing protocol)
    """
    if not url or len(url) < 10: # Shortest possible is github.com/a
        return False
        
    # Pattern explanation:
    # ^(https?://)?     -> Optional http or https
    # (www\.)?          -> Optional www
    # github\.com/      -> Literal github.com/
    # [\w\-\.]+         -> Username (alphanumeric, dots, dashes)
    # (/?[\w\-\.]*)?    -> Optional /repository_name
    # $                 -> End of string
    pattern = r"^(https?://)?(www\.)?github\.com/[\w\-\.]+(/[\w\-\.]+)?$"
    
    return bool(re.match(pattern, url, re.IGNORECASE))