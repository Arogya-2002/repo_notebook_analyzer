from src.components.github_fetcher import GitHubFetcher
from src.pipeline.data_reader_pipeline import initiate_data_reader_pipeline

def initiate_github_fetcher(data_file_path:str):
    fetcher = GitHubFetcher(keywords=['pandas', 'data-analysis'])
    enriched_data = fetcher.process_all_students(initiate_data_reader_pipeline(data_file_path))