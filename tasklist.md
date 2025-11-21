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

- [x] **Task 8: Implement Multithreading for Parallel Idea Processing**
  - [x] Modify `run_pipeline.py` or `core/idea_processor.py` to process at least 8 ideas concurrently using multithreading to improve performance.
  - [x] Make the terminal clean while running only providing essential things like progress etc while the debugging and logging of every step to be in pipeline.log so that any errors or mistakes can be checked.
  - [ ] Also make verification a step in the pipeline after evaluation and also change the code inside the verification folder in core folder as needed but do not change the core logic of verification.
  - [ ] Process a list of ideas, load the schema from schema.json, check each required field, set missing fields to NAN, log debug statements for missing fields, and save the evaluated results in evaluation_results.json ensuring the output matches the schema structure, with all fields present (either with valid data or NAN for missing ones).
  