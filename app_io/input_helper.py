import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class InputHelper:
    """Handles all data input operations."""

    def __init__(self, ideas_filepath: Path, additional_files_dir: Path, rubrics_filepath: Path):
        self.ideas_filepath = ideas_filepath
        self.additional_files_dir = additional_files_dir
        self.rubrics_filepath = rubrics_filepath

    def load_ideas(self) -> List[Dict[str, Any]]:
        """Loads and preprocesses ideas from the main Excel/CSV file."""
        try:
            if self.ideas_filepath.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(self.ideas_filepath)
            else:
                df = pd.read_csv(self.ideas_filepath)
            logger.info(f"✓ Loaded {len(df)} rows from {self.ideas_filepath.name}")
        except Exception as e:
            logger.error(f"✗ Failed to load ideas file: {e}")
            raise

        column_mapping = {
            'Idea Id': 'idea_id',
            'Your idea title': 'idea_title',
            'Brief summary of your Idea': 'brief_summary',
            'Challenge/Business opportunity being addressed and the ability to scale it across TCS and multiple customers.': 'challenge_opportunity',
            'Novelty of the idea, benefits and risks.': 'novelty_benefits_risks',
            'Highlight adherence to Responsible AI principles such as Security, Fairness, Privacy & Legal compliance.': 'responsible_ai',
            'Incase you have a second file that could further illustrate your solution, kindly upload the same here.': 'second_file',
            'Your preferred week of participation': 'preferred_week',
            'Your preference for Build Phase': 'build_preference',
            'Your preference on how you want to  build your idea': 'build_approach',
            'Your preference if you were to develop code': 'code_preference'
        }
        df = df.rename(columns=column_mapping)
        
        if 'idea_id' in df.columns:
            df['idea_id'] = df['idea_id'].astype(str)

        df = df.where(pd.notnull(df), None)
        
        return df.to_dict('records')

    def load_rubrics(self) -> Dict[str, float]:
        """Loads evaluation rubrics from a JSON file."""
        try:
            with open(self.rubrics_filepath, 'r', encoding='utf-8') as f:
                rubrics = json.load(f)
            logger.info(f"✓ Loaded rubrics from {self.rubrics_filepath.name}")
            return rubrics
        except FileNotFoundError:
            logger.error(f"✗ Rubrics file not found at: {self.rubrics_filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"✗ Error decoding JSON from rubrics file: {e}")
            raise

    def get_idea_files_content(self, idea_id: str) -> str:
        """
        Finds all files related to an idea and returns their concatenated content.
        This is a simplified version for reading text-based files. The core
        extraction module will handle complex file types like PDFs and PPTX.
        """
        idea_dir = self.additional_files_dir / str(idea_id)
        if not idea_dir.is_dir():
            logger.warning(f"No directory found for idea ID: {idea_id}")
            return ""

        all_content = []
        for filepath in idea_dir.iterdir():
            if filepath.is_file():
                try:
                    # For now, we will just identify the file path. The core logic will read it.
                    all_content.append(f"FILE:{filepath.resolve()}")
                except Exception as e:
                    logger.error(f"Error processing file {filepath} for idea {idea_id}: {e}")
        
        return "\n".join(all_content)