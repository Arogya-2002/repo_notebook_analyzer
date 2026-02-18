import nbformat
import json
from src.logger import logging
from src.exceptions import CustomException
import sys
from src.entity.config import ConfigEntity,NoteBookAnalyzerConfig
from src.entity.artifacts import NotebookAnalyzerArtifact

class NotebookAnalyzer:
    def __init__(self):
        """
        Initializes the analyzer with filtering constraints.
        """
        self.notebook_analyzer_config = NoteBookAnalyzerConfig(config=ConfigEntity())
        logging.info("NotebookAnalyzer initialized.")

    def _is_important(self, cell_text: str) -> bool:
        """Checks if a code cell contains data science/assignment keywords."""
        return any(keyword.lower() in cell_text.lower() for keyword in self.notebook_analyzer_config.important_keywords)

    def parse_notebook_content(self, raw_bytes: bytes) -> str:
        """
        Converts raw notebook bytes into a filtered text string.
        Optimized for LLM token budget with strict validation.
        """
        try:
            # 1. Immediate guard against empty bytes
            if not raw_bytes or len(raw_bytes.strip()) == 0:
                logging.warning("Received empty byte stream. Skipping notebook parsing.")
                return ""

            # 2. Decode and check for valid JSON start
            content_str = raw_bytes.decode('utf-8').strip()
            if not content_str.startswith('{'):
                logging.error(f"Content is not a valid JSON/Notebook. Starts with: {content_str[:20]}")
                return ""

            nb = nbformat.reads(content_str, as_version=4)
            
            text_output = []
            current_size = 0
            
            # 3. Iterate through cells with filtering logic
            for cell in nb.cells:
                cell_content = ""
                
                # Normalize source text (handle list of strings or single string)
                source = "".join(cell.source) if isinstance(cell.source, list) else cell.source
                
                if cell.cell_type == "markdown":
                    if 0 < len(source) < 500:
                        cell_content = f"[MARKDOWN]\n{source}\n\n"
                
                elif cell.cell_type == "code":
                    if 0 < len(source) <= 1500:
                        if self._is_important(source):
                            cell_content = f"[CODE]\n{source}\n\n"
                
                # 4. Global Budget Check
                if cell_content:
                    # Accessing config dynamically
                    max_chars = self.notebook_analyzer_config.max_notebook_chars
                    if current_size + len(cell_content) > max_chars:
                        logging.warning(f"Max char limit ({max_chars}) reached. Truncating.")
                        break
                    
                    text_output.append(cell_content)
                    current_size += len(cell_content)
            
            return "".join(text_output)

        except nbformat.reader.NotJSONError:
            logging.error("Failed to parse: File is not a valid JSON notebook.")
            return ""
        except Exception as e:
            logging.error(f"Unexpected error during notebook parsing: {e}")
            raise CustomException(e, sys)

    def analyze_all_students(self, enriched_students: list) -> list:
        """
        Orchestrates the parsing for the entire batch.
        """
        logging.info(f"Analyzing notebooks for {len(enriched_students)} students...")
        analyzed_results = []

        for student in enriched_students:
            try:
                # 'raw_content' was provided by our GitHubFetcher
                cleaned_text = self.parse_notebook_content(student['raw_content'])
                
                # Append cleaned text to the student record
                student['notebook_text'] = cleaned_text
                # Remove the raw bytes to keep the object lightweight for the next step
                del student['raw_content'] 
                
                analyzed_results.append(student)
            except Exception as e:
                logging.warning(f"Skipping analysis for {student.get('student_name')}: {e}")
        
        artifact = NotebookAnalyzerArtifact(analyzed_notebook_data=analyzed_results)
        
        return artifact