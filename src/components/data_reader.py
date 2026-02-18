from src.exceptions import CustomException
from src.logger import logging

from src.entity.config import ConfigEntity, DataReaderConfig
from src.entity.artifacts import DataReaderArtifact
from src.utils.github_utils import clean_github_url, is_valid_github_url

import pandas as pd
import re
import sys

class DataReader:
    def __init__(self):
        try:
            logging.info("Initializing DataReader configuration.")
            self.data_reader_config = DataReaderConfig(config=ConfigEntity())
        except Exception as e:
            raise CustomException(e, sys)

    def detect_columns(self, df):
        """
        Detects the column names for student name and github link.
        Returns the ORIGINAL column names from the dataframe.
        """
        try:
            logging.info("Attempting to detect 'Student Name' and 'GitHub Link' columns based on patterns.")
            
            # Map lowercase stripped version -> Original column name
            # This allows us to search loosely but return the exact key pandas needs
            col_map = {str(c).strip().lower(): c for c in df.columns}
            cols_lower = list(col_map.keys())

            # Search in the lowercased keys
            name_col_lower = next((c for c in cols_lower if any(re.search(p, c) for p in self.data_reader_config.name_patterns)), None)
            git_col_lower = next((c for c in cols_lower if any(re.search(p, c) for p in self.data_reader_config.github_patterns)), None)
            
            # Retrieve original column names using the map
            name_col = col_map.get(name_col_lower)
            git_col = col_map.get(git_col_lower)

            if name_col and git_col:
                logging.info(f"Columns successfully detected: Name='{name_col}', GitHub='{git_col}'")
            else:
                logging.warning(f"Column detection failed. Available columns: {list(df.columns)}")

            return name_col, git_col
        except Exception as e:
            raise CustomException(e, sys)

    def load(self, file_path):
        try:
            logging.info(f"Loading Excel file from: {file_path}")
            df = pd.read_excel(file_path).dropna(how='all')
            
            name_col, git_col = self.detect_columns(df)
            
            if not name_col or not git_col:
                error_msg = f"Required columns not found in {list(df.columns)}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
            logging.info("Renaming columns to standard format.")
            return df[[name_col, git_col]].rename(
                columns={name_col: 'student_name', git_col: 'github_link'}
            )
        except Exception as e:
            logging.error(f"Error occurred while loading file: {e}")
            raise CustomException(e, sys)
    
    def initiate_data_reader(self, input_path: str) -> DataReaderArtifact:
        try:
            logging.info("Started Data Reading pipeline.")
            
            # 1. Load & Detect
            df = self.load(input_path)
            initial_count = len(df)
            logging.info(f"Initial data loaded: {initial_count} rows.")

            # 2. Clean & Validate
            logging.info("Cleaning GitHub URLs and validating structure.")
            df['github_link'] = df['github_link'].apply(clean_github_url)
            
            # Filter valid URLs
            valid_mask = df['github_link'].apply(is_valid_github_url)
            df = df[valid_mask]
            
            invalid_count = initial_count - len(df)
            if invalid_count > 0:
                logging.info(f"Removed {invalid_count} invalid GitHub URLs.")

            # 3. Final Deduplication
            prev_len = len(df)
            df = df.drop_duplicates().reset_index(drop=True)
            duplicates_removed = prev_len - len(df)
            
            if duplicates_removed > 0:
                logging.info(f"Removed {duplicates_removed} duplicate records.")
            
            logging.info(f"✅ Pipeline complete: {len(df)} valid records processed.")
            
            # Note: The type hint says DataReaderArtifact, but the logic returns a list of dicts.
            # You might want to wrap this in an Artifact object depending on your system design.
            artifact= DataReaderArtifact( student_records=df.to_dict('records'))
            
            logging.info(f"✅ Pipeline complete: {len(artifact.student_records)} valid records processed.")

            return artifact

        except Exception as e:
            logging.error(f"Data Reader pipeline failed: {e}")
            raise CustomException(e, sys)