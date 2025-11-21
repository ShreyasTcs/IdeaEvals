#!/usr/bin/env python3
"""
Modular Hackathon Evaluation Pipeline
"""

import logging
import sys
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# --- Logging Setup ---
# Configure file handler for detailed logs
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure stream handler for minimal console output (only WARNING and above)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING) # Only show warnings and errors in console
stream_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO), # Base level for all handlers
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

    # --- Configuration and Initialization ---
    ideas_filepath = DATA_DIR / "ideas.xlsx"
    rubrics_filepath = Path(__file__).parent / "config" / "rubrics.json"
    output_filepath = DATA_DIR / "evaluation_results.json"

    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY not found in config. Please set it.")
        return 1

    # 1. Initialize LLM Provider
    # llm_provider = GeminiProvider(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
    llm_provider = AzureOpenAIProvider()

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
    print(f"⚙️  Processing {len(ideas)} ideas concurrently (up to 8 workers)...")
    all_results = []
    
    # Function to wrap process_idea for concurrent execution and error handling
    def process_single_idea(idea):
        try:
            # Pass a copy to avoid side effects in multithreading
            processed_idea = idea_processor.process_idea(
                idea_data=idea.copy(),
                additional_files_dir=ADDITIONAL_FILES_DIR
            )
            return processed_idea
        except Exception as e:
            idea_id = idea.get('idea_id', 'N/A')
            logger.error(f"✗ Failed to process idea {idea_id}: {e}", exc_info=True)
            failed_result = idea.copy()
            failed_result['status'] = 'failed'
            failed_result['error'] = str(e)
            return failed_result

    # Use ThreadPoolExecutor for parallel processing
    MAX_WORKERS = 8 # Process up to 8 ideas concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all ideas to the executor
        future_to_idea = {executor.submit(process_single_idea, idea): idea for idea in ideas}
        
        # Use tqdm to show progress as futures complete
        for future in tqdm(as_completed(future_to_idea), total=len(ideas), desc="Processing Ideas"):
            result = future.result()
            
            # Combine LLM outputs
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
            
            all_results.append(result)
            
            # Save results incrementally
            output_helper.save_results(all_results)

    # --- Final Save ---
    print(f"\n💾 Finalizing results at {output_filepath}...")
    output_helper.save_results(all_results)
    print("✓ Results saved.\n")

    print("✅ Pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
