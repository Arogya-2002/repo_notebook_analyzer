import sys
from src.logger import logging
from src.exceptions import CustomException
from src.components.data_reader import DataReader
from src.components.github_fetcher import GitHubFetcher
from src.components.notebook_analyzer import NotebookAnalyzer
from src.components.llm_analyzer import LlmAnalyzer 
from src.components.report_generator import ReportGenerator

from src.constants import SEARCH_KEYWORDS,ASSIGNMENT_QUESTIONS

def initiate_report_generator_pipeline(data_path: str):
    """
    Orchestrates the full pipeline from data reading to report generation.
    """
    logging.info(">>> Starting Report Generator Pipeline <<<")
    
    # Initialize all components
    try:
        data_reader = DataReader()
        fetcher = GitHubFetcher(keywords=SEARCH_KEYWORDS)
        notebook_analyzer = NotebookAnalyzer()
        llm_analyzer = LlmAnalyzer()
        reporter = ReportGenerator()
        
        
        logging.info(f"Using data source: {data_path}")

        # 1. Read the Excel
        logging.info("Step 1: Initiating data reader...")
        student_records = data_reader.initiate_data_reader(data_path)
        
        # 2. Fetch from GitHub
        logging.info("Step 2: Fetching repositories and notebooks from GitHub...")
        fetcher_artifact = fetcher.process_all_students(student_records)
        if not fetcher_artifact.notebook_data:
            logging.warning("No notebooks were successfully fetched. Pipeline may result in an empty report.")
        
        # 3. Extract & Filter Notebook Content
        logging.info("Step 3: Analyzing and filtering notebook content...")
        analyzer_artifact = notebook_analyzer.analyze_all_students(fetcher_artifact.notebook_data)
        
        # 4. Generate LLM Analysis
        logging.info("Step 4: Running LLM evaluation (this may take a while based on rate limits)...")
        final_report_artifact = llm_analyzer.run_evaluation(
            analyzer_artifact.analyzed_notebook_data,
            assignment_questions=ASSIGNMENT_QUESTIONS
        )
        
        # 5. Generate Final Report
        logging.info("Step 5: Generating final Excel report...")
        report_path = reporter.generate_report(final_report_artifact)
        
        logging.info(f"✅ Pipeline Completed Successfully. Report saved at: {report_path}")
        return report_path

    except Exception as e:
        logging.error(f"❌ Pipeline Failed at an orchestration level: {str(e)}")
        raise CustomException(e, sys)