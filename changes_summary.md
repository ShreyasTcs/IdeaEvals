# Backend Refactoring Summary

This document summarizes the changes made to the backend to improve modularity and organization.

## Directory Structure Changes

- **`prompts` directory created:** All LLM prompts have been moved to this directory to separate them from the application logic.
- **`utils` directory created:** Shared utility functions have been moved to this directory to improve code reuse.

## Core Module Refactoring

- **`core/idea_processor.py`:**
    - Evaluation prompts moved to `prompts/evaluation_system_prompt.txt` and `prompts/evaluation_user_prompt.txt`.
    - The module now reads the prompts from the new files.
- **`core/classification/tcs_classifier.py`:**
    - The main system prompt has been moved to `prompts/classification_system_prompt.txt`.
    - The `INDUSTRIES` dictionary has been moved to `utils/industries.py`.
    - The `_call_llm` and `_parse_json` utility functions have been moved to `utils/llm_utils.py`.
    - The module has been refactored to import and use the new modules and prompts.
- **`core/evaluation/idea_evaluator.py`:**
    - The `RESPONSE_FORMAT_INSTRUCTION` prompt has been moved to `prompts/evaluation_response_format.txt`.
    - The module now reads the prompt from the new file.
- **`core/extraction/file_extractor.py`:**
    - All prompts for analyzing files have been moved to the `prompts` directory.
    - File processing utility functions have been moved to `utils/file_utils.py`.
    - The module has been refactored to import and use the new modules and prompts.

## Task List Update

- The task in `tasklist.md` has been marked as complete.
