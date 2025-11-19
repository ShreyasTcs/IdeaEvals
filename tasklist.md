# Backend Refactoring Task List

This file tracks the progress of refactoring the backend to be modular and independent of specific data sources or LLM providers.

- [x] **Task 1: Create the LLM Abstraction Layer**
  - [x] Create a new `llm` directory.
  - [x] Define a base `LLMProvider` class in `llm/llm_provider.py`
  - [x] Implement a `GeminiProvider` class in `llm/gemini_provider.py`.
  - [x] Create a placeholder `AzureOpenAIProvider` class in `llm/azure_openai_provider.py`.

- [x] **Task 2: Create I/O Helper Classes**
  - [x] Create a new `io` directory.
  - [x] Implement `InputHelper` in `io/input_helper.py`.
  - [x] Implement `OutputHelper` in `io/output_helper.py`.

- [x] **Task 3: Isolate the Core Processing Logic**
  - [x] Create a new `core` directory.
  - [x] Move `classification`, `extraction`, and `evaluation` into `core`.
  - [x] Refactor modules in `core` to remove direct data access and use the `LLMProvider`.
  - [x] Create `IdeaProcessor` in `core/idea_processor.py`.

- [x] **Task 4: Update the Main Application Orchestrator**
  - [x] Refactor `run_pipeline.py` to use the new `llm`, `io`, and `core` modules.

- [x] **Task 5: Clean Up Old Modules**
  - [x] Delete the `database` directory.
  - [x] Delete the `pipeline` directory.

# New Tasks (November 19, 2025)

- [ ] **Task 6: Fix Video File Parsing**
  - [ ] Investigate `core/extraction/file_extractor.py` and `core/extraction/content_processor.py` to understand why video files are not being parsed.
  - [ ] Implement or integrate a solution for extracting content from video files (e.g., transcribing audio, extracting keyframes/metadata).

- [ ] **Task 7: Fix Evaluation Failure**
  - [ ] Debug `core/evaluation/idea_evaluator.py` to identify why evaluation scores are consistently "Parsing failed".
  - [ ] Verify interaction with `llm/llm_provider.py` and `config/rubrics.json` to ensure correct data flow and parsing of LLM responses.

- [ ] **Task 8: Implement Multithreading for Parallel Idea Processing**
  - [ ] Modify `run_pipeline.py` or `core/idea_processor.py` to process at least 8 ideas concurrently using multithreading to improve performance.