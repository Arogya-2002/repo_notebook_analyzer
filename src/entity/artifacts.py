from dataclasses import dataclass
from typing import Dict,List

@dataclass
class DataReaderArtifact:
    student_records:Dict

@dataclass
class GitHubFetcherArtifact:
    notebook_data:List

@dataclass
class NotebookAnalyzerArtifact:
    analyzed_notebook_data:List

@dataclass
class LlmAnalyzerArtifact:
    evaluation_results:List