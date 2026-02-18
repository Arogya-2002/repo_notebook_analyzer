from src.components.data_reader import DataReader
from src.components.github_fetcher import GitHubFetcher
from src.components.notebook_analyzer import NotebookAnalyzer
from src.components.llm_analyzer import LlmAnalyzer  # New Import

if __name__ == "__main__":
    # Initialize all components
    data_reader = DataReader()
    fetcher = GitHubFetcher(keywords=['pandas', 'analysis', 'assignment', 'data'])
    notebook_analyzer = NotebookAnalyzer()
    llm_analyzer = LlmAnalyzer() # Initialize the LLM component
    
    DATA_PATH = "/workspaces/repo_notebook_analyzer/students_list.xlsx"
    
    # Optional: Define specific questions for this assignment
    ASSIGNMENT_QUESTIONS = """
    1. Did the student perform proper data cleaning (handling nulls)?
    2. Are there at least 2 meaningful visualizations?
    3. Is there a clear conclusion derived from the data?
    """
    
    try:
        # 1. Read the Excel
        student_records = data_reader.initiate_data_reader(DATA_PATH)
        
        # 2. Fetch from GitHub (Directly or via fallback search)
        fetcher_artifact = fetcher.process_all_students(student_records)
        
        # 3. Extract & Filter Notebook Content
        analyzer_artifact = notebook_analyzer.analyze_all_students(fetcher_artifact.notebook_data)
        
        # 4. Generate LLM Analysis (The Final Step)
        final_report_artifact = llm_analyzer.run_evaluation(
            analyzer_artifact.analyzed_notebook_data,
            assignment_questions=ASSIGNMENT_QUESTIONS
        )
        
        # 5. Output the results
        print("\n" + "="*50)
        print("📊 FINAL STUDENT EVALUATION REPORTS")
        print("="*50)
        
        for record in final_report_artifact.evaluation_results:
            print(f"\nSTUDENT: {record['student_name']}")
            print(f"REPO: {record['repo_name']}")
            print("-" * 30)
            print(record['llm_report']) # This contains the Summary, Positives, and Negatives
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")