from src.constants import *
from src.constants.prompts import *

class ConfigEntity:
    def __init__(self):
        self.name_patterns = NAME_PATTERNS
        self.github_patterns = GITHUB_PATTERNS
        self.github_url_patterns = GITHUB_URL_PATTERNS

        self.github_token = GITHUB_TOKEN

        self.important_keywords = IMPORTANT_KEYWORDS
        self.max_notebook_chars = MAX_NOTEBOOK_CHARS

        self.grok_api_key = GROQ_API_KEY
        self.unified_evaluation_prompt = UNIFIED_EVALUATION_PROMPT
        self.model_name = MODEL_NAME
        self.max_output_tokens = MAX_OUTPUT_TOKENS
        self.delay_between_students = DELAY_BETWEEN_STUDENTS

        self.output_file_name = OUTPUT_FILE_NAME

        self.search_keywords = SEARCH_KEYWORDS
        self.assignment_questions = ASSIGNMENT_QUESTIONS


class DataReaderConfig:
    def __init__(self,config:ConfigEntity):
        self.name_patterns = config.name_patterns
        self.github_patterns = config.github_patterns
        self.github_url_patterns = config.github_url_patterns

class GitHubFetcherConfig:
    def __init__(self,config:ConfigEntity):
        self.github_token = config.github_token

class NoteBookAnalyzerConfig:
    def __init__(self,config:ConfigEntity):
        self.important_keywords = config.important_keywords
        self.max_notebook_chars = config.max_notebook_chars

class LlmAnalyzerConfig:
    def __init__(self,config:ConfigEntity):
        self.groq_api_key = config.grok_api_key
        self.unified_evaluation_prompt = config.unified_evaluation_prompt
        self.model_name = config.model_name
        self.max_output_tokens = int(config.max_output_tokens)
        self.delay_between_students = int(config.delay_between_students)

class ReportGeneratorConfig:
    def __init__(self,config:ConfigEntity):
        self.output_file_name = config.output_file_name