import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OUTPUT_FILE_NAME = "students_list.xlsx"


GITHUB_URL_PATTERNS =[
    r'^https?://github\.com/[a-zA-Z0-9_-]+/?$',
        r'^https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+/?$',
        r'^[a-zA-Z0-9_-]+$',  # Just username
        r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+$',
]

NAME_PATTERNS = [
        r'.*name.*', r'.*student.*', r'.*user.*', r'.*person.*',
        r'full.?name', r'first.?name', r'last.?name', r'student.?name'
    ]

    # Possible GitHub column patterns
GITHUB_PATTERNS = [
        r'.*github.*', r'.*repo.*', r'.*link.*', r'.*url.*',
        r'.*profile.*', r'.*account.*', r'git.*link'
    ]