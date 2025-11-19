import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OutputHelper:
    """Handles all data output operations."""

    def __init__(self, output_filepath: Path):
        self.output_filepath = output_filepath

    def save_results(self, results: List[Dict[str, Any]]):
        """
        Saves the list of processed idea results to a single JSON file.
        """
        try:
            self.output_filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logger.info(f"✓ Successfully saved {len(results)} results to {self.output_filepath}")
        except Exception as e:
            logger.error(f"✗ Failed to save results to {self.output_filepath}: {e}")
            raise
