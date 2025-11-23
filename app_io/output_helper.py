import json
from pathlib import Path
from typing import List, Dict, Any
import logging
import os
import math

logger = logging.getLogger(__name__)

class OutputHelper:
    """Handles all data output operations."""

    def __init__(self, output_filepath: Path):
        self.output_filepath = output_filepath
        # Ensure the output directory exists
        self.output_filepath.parent.mkdir(parents=True, exist_ok=True)

    def _clean_nan_values(self, obj: Any) -> Any:
        """
        Recursively converts NaN float values to None in dictionaries and lists.
        """
        if isinstance(obj, dict):
            return {k: self._clean_nan_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_nan_values(elem) for elem in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        return obj

    def save_results(self, results: List[Dict[str, Any]]):
        """
        Saves the list of processed idea results to a single JSON file.
        """
        try:
            cleaned_results = self._clean_nan_values(results)
            with open(self.output_filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_results, f, indent=4, ensure_ascii=False)
            logger.info(f"✓ Successfully saved {len(results)} results to {self.output_filepath}")
        except Exception as e:
            logger.error(f"✗ Failed to save results to {self.output_filepath}: {e}")
            raise

    def save_result_incrementally(self, result: Dict[str, Any]):
        """
        Saves a single result to the JSON output file, appending if the file exists.
        """
        try:
            results = []
            if self.output_filepath.exists() and os.path.getsize(self.output_filepath) > 0:
                with open(self.output_filepath, 'r', encoding='utf-8') as f:
                    try:
                        results = json.load(f)
                        if not isinstance(results, list):
                            logger.warning(f"Output file {self.output_filepath} does not contain a JSON list. Starting fresh.")
                            results = []
                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON from {self.output_filepath}. Starting fresh.")
                        results = []
            
            cleaned_result = self._clean_nan_values(result)
            results.append(cleaned_result)
            
            with open(self.output_filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logger.info(f"✓ Appended result for idea {result.get('idea_id', 'N/A')} to {self.output_filepath}")

        except Exception as e:
            logger.error(f"✗ Failed to save incremental result to {self.output_filepath}: {e}")
            raise
