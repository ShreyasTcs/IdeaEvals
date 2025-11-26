#!/usr/bin/env python3
"""
Modular Hackathon Evaluation Pipeline
"""

import logging
import sys
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
import time

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.config import (
    GEMINI_API_KEY, GEMINI_MODEL, DATA_DIR,
    ADDITIONAL_FILES_DIR, LOG_FILE, LOG_LEVEL
)
from llm.gemini_provider import GeminiProvider
from llm.azure_openai_provider import AzureOpenAIProvider
from app_io.input_helper import InputHelper
from app_io.output_helper import OutputHelper
from core.idea_processor import IdeaProcessor
from utils.db_helper import DBHelper

# --- Logging Setup ---
# Configure file handler for detailed logs
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure stream handler for minimal console output (only WARNING and above)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
stream_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),  # Base level for all handlers
    handlers=[
        file_handler,
        stream_handler
    ]
)
logger = logging.getLogger(__name__)

# --- Main Application ---
def main():
    """Main pipeline execution."""
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    print("\n" + "="*80)
    print("🎯 MODULAR HACKATHON EVALUATION PIPELINE")
    print("="*80 + "\n")

    parser = argparse.ArgumentParser(description="Modular Hackathon Evaluation Pipeline")
    parser.add_argument('--ideas_filepath', type=Path, required=True, help="Path to the ideas XLSX file.")
    parser.add_argument('--rubrics_filepath', type=Path, required=True, help="Path to the rubrics JSON file.")
    parser.add_argument('--output_filepath', type=Path, required=True, help="Path to the output JSON file.")
    parser.add_argument('--progress_filepath', type=Path, help="Path to where progress should be stored.")
    parser.add_argument('--hackathon_name', type=str, default="Hackathon", help="Name of the hackathon.")
    parser.add_argument('--hackathon_description', type=str, default="", help="Description of the hackathon.")
    args = parser.parse_args()

    # --- DB Setup ---
    db_helper = DBHelper()
    try:
        db_helper.create_tables()
    except Exception as e:
        logger.error(f"Database setup failed: {e}")

    # --- Configuration and Initialization ---
    ideas_filepath = args.ideas_filepath
    rubrics_filepath = args.rubrics_filepath
    output_filepath = args.output_filepath
    progress_filepath = args.progress_filepath

    def update_progress(processed, total, status, error=None, eta_seconds=None):
        if progress_filepath:
            progress_data = {
                'processed_ideas': processed,
                'total_ideas': total,
                'status': status
            }
            if error:
                progress_data['error'] = str(error)
            
            if eta_seconds is not None:
                mins, secs = divmod(eta_seconds, 60)
                progress_data['estimated_time_remaining'] = f"{int(mins)}m {int(secs)}s"
            else:
                progress_data['estimated_time_remaining'] = "Calculating..."

            try:
                with open(progress_filepath, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f)
            except Exception as e:
                logger.warning(f"Could not write to progress file {progress_filepath}: {e}")

    # --- LLM Provider Initialization ---
    try:
        llm_provider = AzureOpenAIProvider()
        logger.info("Using AzureOpenAIProvider.")
    except ValueError as e:
        logger.warning(f"Azure OpenAI not fully configured: {e}. Attempting to use GeminiProvider.")
        if GEMINI_API_KEY:
            llm_provider = GeminiProvider(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
            logger.info("Using GeminiProvider.")
        else:
            logger.error("❌ No LLM provider is configured.")
            update_progress(0, 0, 'failed', "No LLM provider is configured.")
            return 1

    # --- I/O Helpers ---
    input_helper = InputHelper(ideas_filepath=ideas_filepath, additional_files_dir=ADDITIONAL_FILES_DIR, rubrics_filepath=rubrics_filepath)
    output_helper = OutputHelper(output_filepath=output_filepath)

    # --- Data Loading ---
    try:
        print("📂 Loading input data...")
        ideas = input_helper.load_ideas()
        rubrics = input_helper.load_rubrics()
        total_ideas = len(ideas)
        print(f"✓ Loaded {total_ideas} ideas and {len(rubrics)} rubric criteria.\n")
        update_progress(0, total_ideas, 'processing')
    except Exception as e:
        logger.error(f"Failed to load initial data: {e}")
        update_progress(0, 0, 'failed', f"Failed to load initial data: {e}")
        return 1

    # --- Setup Hackathon in DB ---
    print("💾 Setting up Hackathon in Database...")
    hackathon_id, rubric_map = db_helper.setup_hackathon(args.hackathon_name, args.hackathon_description, rubrics)
    if hackathon_id:
        print(f"✓ Hackathon setup complete. ID: {hackathon_id}")
    else:
        print("⚠ Failed to setup Hackathon in DB. Data will only be saved to JSON.")

    # --- Core Processor ---
    idea_processor = IdeaProcessor(llm_provider=llm_provider, rubrics=rubrics)

    # --- Processing Loop ---
    print(f"⚙️  Processing {total_ideas} ideas concurrently (up to 8 workers)...")
    
    def process_single_idea(idea):
        try:
            return idea_processor.process_idea(idea_data=idea.copy(), additional_files_dir=ADDITIONAL_FILES_DIR)
        except Exception as e:
            idea_id = idea.get('idea_id', 'N/A')
            logger.error(f"✗ Failed to process idea {idea_id}: {e}", exc_info=True)
            failed_result = idea.copy()
            failed_result['status'] = 'failed'
            failed_result['error'] = str(e)
            return failed_result

    all_results = []
    processed_ideas_count = 0
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_idea = {executor.submit(process_single_idea, idea): idea for idea in ideas}
        for future in tqdm(as_completed(future_to_idea), total=len(ideas), desc="Processing Ideas"):
            result = future.result()
            
            llm_output = {
                "extracted_files_content": result.pop('extracted_files_content', ''),
                "content_type": result.pop('content_type', 'unknown'),
                "theme": result.pop('theme', {}),
                "industry": result.pop('industry', {}),
                "technologies": result.pop('technologies', {}),
                "evaluation": result.pop('evaluation', {}),
                "verification": result.pop('verification', {})
            }
            result['llm_output'] = llm_output
            
            # Save JSON incrementally
            output_helper.save_result_incrementally(result)
            all_results.append(result)

            # Save to DB incrementally
            if hackathon_id:
                db_helper.insert_single_idea(hackathon_id, result, rubric_map)
            
            processed_ideas_count += 1
            
            # ETA calculation
            elapsed_time = time.time() - start_time
            avg_time_per_idea = elapsed_time / processed_ideas_count
            remaining_ideas = total_ideas - processed_ideas_count
            eta_seconds = avg_time_per_idea * remaining_ideas
            update_progress(processed_ideas_count, total_ideas, 'processing', eta_seconds=eta_seconds)

    # --- Finalization ---
    print(f"\n💾 Results have been incrementally saved to {output_filepath}")
    update_progress(processed_ideas_count, total_ideas, 'completed', eta_seconds=0)

    if hackathon_id:
        print(f"\n✓ All results stored in database for Hackathon ID: {hackathon_id}")
        # Optionally, generate the final JSON from the DB
        json_from_db = db_helper.get_results_as_json(hackathon_id)
        db_json_output_path = output_filepath.parent / f"db_results_{hackathon_id}.json"
        try:
            with open(db_json_output_path, 'w') as f:
                f.write(json_from_db)
            print(f"✓ JSON output from database saved to {db_json_output_path}")
        except Exception as e:
            logger.error(f"Failed to write DB output file: {e}")

    print("\n✅ Pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Pipeline failed with unhandled exception: {e}", exc_info=True)
        # Try to update progress file on catastrophic failure
        parser = argparse.ArgumentParser()
        parser.add_argument('--progress_filepath', type=Path)
        args, _ = parser.parse_known_args()
        if args.progress_filepath:
            try:
                with open(args.progress_filepath, 'w') as f:
                    json.dump({'processed_ideas': 0, 'total_ideas': 0, 'status': 'failed', 'error': str(e)}, f)
            except Exception as write_e:
                logger.error(f"Could not write final error to progress file {args.progress_filepath}: {write_e}")
        sys.exit(1)
