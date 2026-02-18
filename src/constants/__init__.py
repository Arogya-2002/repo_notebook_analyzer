import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
MAX_OUTPUT_TOKENS = os.getenv("MAX_OUTPUT_TOKENS")
DELAY_BETWEEN_STUDENTS = os.getenv("DELAY_BETWEEN_STUDENTS")

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

IMPORTANT_KEYWORDS =[
        # Data Analysis & SQL
        "select", "from", "where", "group by", "order by", "join", "inner join", "left join",
        "sum", "count", "avg", "max", "min", "distinct",
        "pandas", "pd.", "read_csv", "read_excel", "read_sql",
        "sqlalchemy", "sqlite", "postgresql", "mysql",
        
        # Data Manipulation
        "dropna", "fillna", "isnull", "notnull",
        "groupby", "merge", "join", "concat", "pivot",
        
        # Visualization
        "matplotlib", "seaborn", "plt.", "plot", "bar", "hist", "scatter",
        
        # Statistics & Analysis
        "numpy", "np.", "scipy", "stats",
        "correlation", "regression", "trend", "forecast",
        
        # Business Intelligence terms
        "revenue", "sales", "profit", "margin", "kpi", "metric",
        "customer", "segment", "cohort", "retention", "churn",
        "transaction", "purchase", "order", "invoice"
    ]

MAX_NOTEBOOK_CHARS = 5000