import os
import sys
import time
from typing import List, Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

from src.logger import logging
from src.exceptions import CustomException
from src.entity.config import ConfigEntity, LlmAnalyzerConfig
from src.entity.artifacts import LlmAnalyzerArtifact


load_dotenv()

class LlmAnalyzer:
    def __init__(self):
        """
        Initializes the LLMAnalyzer with Groq client and config.
        """
        try:
            self.llm_analyzer_config = LlmAnalyzerConfig(config=ConfigEntity())
            
            if not self.llm_analyzer_config.groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables.")
                
            self.client = Groq(api_key=self.llm_analyzer_config.groq_api_key)
            logging.info(f"LLMAnalyzer initialized using model: {self.llm_analyzer_config.model_name}")
        except Exception as e:
            raise CustomException(e, sys)

    def _get_unified_analysis(self, notebook_text: str, questions: Optional[str] = None) -> str:
        """
        Performs technical summary and evaluation in a single API call.
        """
        try:
            # Throttle to stay within Groq TPM/RPM limits
            time.sleep(self.llm_analyzer_config.delay_between_students)
            
            # Format prompts from constants
            questions_block = f"\nSPECIFIC ANALYSIS QUESTIONS:\n{questions}" if questions else ""
            system_prompt = self.llm_analyzer_config.unified_evaluation_prompt.format(questions_block=questions_block)

            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Notebook Content:\n\n{notebook_text}"}
                ],
                model=self.llm_analyzer_config.model_name,
                temperature=0.2, # Low temperature for more objective grading
                max_tokens=self.llm_analyzer_config.max_output_tokens,
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Groq API Error: {e}")
            return f"ANALYSIS_ERROR: The model was unable to process this notebook. {str(e)}"

    def run_evaluation(self, notebook_data_list: List[Dict[str, Any]], assignment_questions: Optional[str] = None) -> LlmAnalyzerArtifact:
        """
        Orchestrates the unified evaluation for the entire batch.
        """
        logging.info(f"Starting Unified LLM Evaluation for {len(notebook_data_list)} students...")
        final_evaluations = []

        

        for student in notebook_data_list:
            student_name = student.get('student_name', 'Unknown Student')
            logging.info(f"Processing evaluation for: {student_name}")

            try:
                # Execute the single-call analysis
                llm_report = self._get_unified_analysis(
                    student.get('notebook_text', ''), 
                    assignment_questions
                )

                # Append results while maintaining previous metadata
                report_record = {
                    **student,
                    "llm_report": llm_report
                }
                
                final_evaluations.append(report_record)

            except Exception as e:
                logging.error(f"Pipeline failure for student {student_name}: {e}")
                continue

        logging.info("✅ LLM Analysis pipeline complete.")
        artifact = LlmAnalyzerArtifact(evaluation_results=final_evaluations)
        return artifact