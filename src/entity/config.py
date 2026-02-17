from src.constants import *

class ConfigEntity:
    def __init__(self):
        self.name_patterns = NAME_PATTERNS
        self.github_patterns = GITHUB_PATTERNS
        self.github_url_patterns = GITHUB_URL_PATTERNS


class DataReaderConfig:
    def __init__(self,config:ConfigEntity):
        self.name_patterns = config.name_patterns
        self.github_patterns = config.github_patterns
        self.github_url_patterns = config.github_url_patterns