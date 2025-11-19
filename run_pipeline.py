#!/usr/bin/env python3
"""
Modular Hackathon Evaluation Pipeline
"""

import logging
import sys
from pathlib import Path
from tqdm import tqdm

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.config import (
    GEMINI_API_KEY, GEMINI_MODEL, DATA_DIR,
    ADDITIONAL_FILES_DIR, LOG_FILE, LOG_LEVEL
)
from llm.gemini_provider import GeminiProvider
from app_io.input_helper import InputHelper
from app_io.output_helper import OutputHelper
from core.idea_processor import IdeaProcessor

# --- Logging Setup ---
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Main Application ---
def main():
    """Main pipeline execution."""
    print("\n" + "="*80)
    print("🎯 MODULAR HACKATHON EVALUATION PIPELINE")
    print("="*80 + "\n")

    # --- Configuration and Initialization ---
    ideas_filepath = DATA_DIR / "ideas.xlsx"
    rubrics_filepath = Path(__file__).parent / "config" / "rubrics.json"
    output_filepath = DATA_DIR / "evaluation_results.json"

    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY not found in config. Please set it.")
        return 1

    # 1. Initialize LLM Provider
    llm_provider = GeminiProvider(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    # 2. Initialize I/O Helpers
    input_helper = InputHelper(
        ideas_filepath=ideas_filepath,
        additional_files_dir=ADDITIONAL_FILES_DIR,
        rubrics_filepath=rubrics_filepath
    )
    output_helper = OutputHelper(output_filepath=output_filepath)

    # --- Data Loading ---
    try:
        print("📂 Loading input data...")
        ideas = input_helper.load_ideas()
        rubrics = input_helper.load_rubrics()
        print(f"✓ Loaded {len(ideas)} ideas and {len(rubrics)} rubric criteria.\n")
    except Exception as e:
        logger.error(f"Failed to load initial data: {e}")
        return 1

    # 3. Initialize the Core Processor
    idea_processor = IdeaProcessor(llm_provider=llm_provider, rubrics=rubrics)

    # --- Processing Loop ---
    print(f"⚙️  Processing {len(ideas)} ideas...")
    all_results = []
    
    for idea in tqdm(ideas, desc="Processing Ideas"):
        try:
            processed_idea = idea_processor.process_idea(
                idea_data=idea.copy(), # Pass a copy to avoid side effects
                additional_files_dir=ADDITIONAL_FILES_DIR
            )
            all_results.append(processed_idea)
        except Exception as e:
            logger.error(f"✗ Failed to process idea {idea.get('idea_id', 'N/A')}: {e}", exc_info=True)
            # Optionally, add a failed record to the results
            failed_result = idea.copy()
            failed_result['status'] = 'failed'
            failed_result['error'] = str(e)
            all_results.append(failed_result)

    # --- Save Results ---
    print(f"\n💾 Saving results to {output_filepath}...")
    output_helper.save_results(all_results)
    print("✓ Results saved.\n")

    print("✅ Pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
