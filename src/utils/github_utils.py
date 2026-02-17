import re
import pandas as pd

def is_valid_github_url(url: str) -> bool:
    if not url or pd.isna(url): return False
    # Strict GitHub username/repo regex
    patterns = [
        r'^https?://github\.com/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}/?$',
        r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$'
    ]
    return any(re.match(p, str(url), re.I) for p in patterns)

def clean_github_url(url: str) -> str:
    if not url or pd.isna(url): return ""
    url = str(url).strip().lower()
    url = re.sub(r'^(https?://)?(www\.)?github\.com/', '', url)
    url = url.split('/tree/')[0].split('/blob/')[0].rstrip('/')
    return f"https://github.com/{url}" if url else ""