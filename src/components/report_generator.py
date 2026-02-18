import pandas as pd
import re
import json
import os
from src.logger import logging
from src.entity.artifacts import LlmAnalyzerArtifact
from src.entity.config import ReportGeneratorConfig,ConfigEntity

class ReportGenerator:
    def __init__(self):
        self.report_generator_config = ReportGeneratorConfig(config=ConfigEntity())
        # Ensure the directory exists
        self._create_output_dir()
        logging.info(f"ReportGenerator initialized. Target: {self.report_generator_config.output_file_name}")

    def _create_output_dir(self):
        """Creates the parent directory if it does not exist."""
        dir_name = os.path.dirname(self.report_generator_config.output_file_name)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            logging.info(f"Created output directory: {dir_name}")

    def _smart_parse_llm_response(self, response_text: str) -> dict:
        """Parses JSON or Plain Text LLM responses into structured feedback."""
        sections = {"Positives": "N/A", "Negatives": "N/A", "Improvements": "N/A"}
        if not response_text:
            return sections

        # 1. JSON Detection & Parsing
        if "```json" in response_text or response_text.strip().startswith("{"):
            try:
                json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                    for key, target in [("POSITIVES", "Positives"), ("NEGATIVES", "Negatives"), ("IMPROVEMENTS", "Improvements")]:
                        val = data.get(key, [])
                        sections[target] = "\n".join(val) if isinstance(val, list) else str(val)
                    return sections
            except Exception as e:
                logging.warning(f"JSON parsing failed, falling back to regex: {e}")

        # 2. Text/Regex Parsing
        patterns = {
            "Positives": r"POSITIVES:\s*(.*?)(?=NEGATIVES:|IMPROVEMENTS:|Based on|$)",
            "Negatives": r"NEGATIVES:\s*(.*?)(?=POSITIVES:|IMPROVEMENTS:|Based on|$)",
            "Improvements": r"IMPROVEMENTS:\s*(.*?)(?=POSITIVES:|NEGATIVES:|Based on|$)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[key] = match.group(1).strip()

        return sections

    def generate_report(self, artifact: LlmAnalyzerArtifact):
        """Converts LLM results into a formatted Excel spreadsheet."""
        logging.info("Starting Excel generation...")
        
        results = artifact.evaluation_results
        final_data = []

        for entry in results:
            parsed_feedback = self._smart_parse_llm_response(entry.get('llm_report', ''))
            
            row = {
                "Student Name": entry.get('student_name'),
                "GitHub Link": entry.get('github_link'), # <--- This will now find the URL
                "Repo Name": entry.get('repo_name'),
                "Notebook": entry.get('notebook_name'),
                "Positives": parsed_feedback["Positives"],
                "Negatives": parsed_feedback["Negatives"],
                "Improvements": parsed_feedback["Improvements"]
            }
            final_data.append(row)

        df = pd.DataFrame(final_data)

        

        try:
            with pd.ExcelWriter(self.report_generator_config.output_file_name, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Evaluations', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['Evaluations']

                # Styles
                cell_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
                header_format = workbook.add_format({'bold': True, 'bg_color': '#CFE2F3', 'border': 1, 'align': 'center'})

                # Column Widths
                worksheet.set_column('A:A', 20) # Name
                worksheet.set_column('B:B', 30) # Link
                worksheet.set_column('C:D', 20) # Repo/Notebook
                worksheet.set_column('E:G', 50, cell_format) # Feedback columns

                # Write Headers with Format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

            logging.info(f"✅ Report successfully generated at: {os.path.abspath(self.report_generator_config.output_file_name)}")
            return self.report_generator_config.output_file_name

        except Exception as e:
            logging.error(f"Error during Excel export: {e}")
            return None