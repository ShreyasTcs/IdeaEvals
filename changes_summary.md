# Project Overview: IdeaEvals

This document provides a summary of the current architecture, system flow, code structure, and instructions on how to run the IdeaEvals application. Please note that this summary does not include a history of specific changes made over time, as that information is not available in this context.

## System Architecture

The IdeaEvals system is designed to process, classify, and evaluate ideas, often involving content extraction and leveraging Large Language Models (LLMs). Its architecture is modular, separating concerns into distinct components:

*   **Core Processing (`core/`):** Contains the main business logic for idea processing, classification, evaluation, and content extraction.
    *   `idea_processor.py`: Orchestrates the overall idea processing workflow.
    *   `classification/`: Handles the categorization of ideas.
        *   `tcs_classifier.py`: Implements the classification logic.
        *   `theme_definitions.py`: Defines the themes or categories for classification.
    *   `evaluation/`: Manages the evaluation of ideas based on defined rubrics.
        *   `idea_evaluator.py`: Contains the logic for evaluating ideas.
    *   `extraction/`: Responsible for extracting content from various file types.
        *   `content_processor.py`: Processes extracted content.
        *   `file_extractor.py`: Extracts raw content from files (e.g., PDFs, PPTXs).
*   **Input/Output (`io/`):** Manages data ingress and egress.
    *   `input_helper.py`: Handles reading input data (e.g., from `ideas.xlsx`).
    *   `output_helper.py`: Manages writing processed and evaluated data.
*   **LLM Integration (`llm/`):** Provides an abstraction layer for interacting with different Large Language Models.
    *   `llm_provider.py`: Defines the interface for LLM interactions.
    *   `azure_openai_provider.py`: Implements the LLM provider for Azure OpenAI.
    *   `gemini_provider.py`: Implements the LLM provider for Google Gemini.
*   **Configuration (`config/`):** Stores system configurations, schemas, and rubrics.
    *   `config.py`: Contains general application settings.
    *   `rubrics.json`: Defines the criteria and scoring for idea evaluation.
    *   `schema.json`: Specifies data schemas for validation.
*   **Data (`data/`):** Holds input data files and additional resources.
    *   `ideas.xlsx`: Primary spreadsheet containing ideas for processing.
    *   `additional_files/`: Directory for supplementary files related to ideas (e.g., PDFs, PPTXs, videos).
*   **Verification (`verification/`):** Contains tools and tests for verifying the system's output and functionality.
    *   `generate_verification_report.py`: Generates reports to verify evaluation results.
    *   `test_evaluation_verification.py`: Unit/integration tests for the evaluation process.
*   **Main Entry Point (`run_pipeline.py`):** The script that orchestrates the entire pipeline execution.

## System Flow

The typical flow of the IdeaEvals system is as follows:

1.  **Initialization:** The `run_pipeline.py` script starts, loading configurations from `config/`.
2.  **Input Data Loading:** `io/input_helper.py` reads initial idea data, typically from `data/ideas.xlsx`.
3.  **Content Extraction:** For ideas with associated files in `data/additional_files/`, `core/extraction/file_extractor.py` extracts relevant content. This content is then processed by `core/extraction/content_processor.py`.
4.  **Idea Processing:** `core/idea_processor.py` takes the raw idea data and extracted content, preparing it for further steps.
5.  **Classification:** `core/classification/tcs_classifier.py` uses `theme_definitions.py` and potentially an LLM (via `llm/llm_provider.py`) to classify each idea into predefined categories.
6.  **Evaluation:** `core/evaluation/idea_evaluator.py` evaluates the processed and classified ideas against the rubrics defined in `config/rubrics.json`, often utilizing an LLM for nuanced scoring.
7.  **Output Generation:** `io/output_helper.py` writes the classified and evaluated ideas to a specified output format (e.g., an updated spreadsheet or a report).
8.  **Verification (Optional):** `verification/generate_verification_report.py` can be run to analyze the output and ensure the evaluations meet quality standards.

## Code Explanation (Brief)

*   **`run_pipeline.py`**: The main script that ties all components together. It defines the sequence of operations from input to output.
*   **`config/`**: Python modules and JSON files defining constants, parameters, and structured data for the application.
*   **`core/`**: 
    *   `idea_processor.py`: High-level logic for managing the lifecycle of an idea through the system.
    *   `classification/`: Contains algorithms and data structures for categorizing ideas.
    *   `evaluation/`: Implements the scoring and assessment logic based on criteria.
    *   `extraction/`: Handles parsing and extracting textual and other data from various document types.
*   **`io/`**: Utility functions for reading from and writing to different data sources and sinks.
*   **`llm/`**: Abstraction layer for interacting with different LLM APIs, allowing for easy switching between providers like Azure OpenAI and Gemini.
*   **`data/`**: Contains sample or actual input data and any supplementary files.
*   **`verification/`**: Scripts and tests to ensure the correctness and quality of the system's output, especially the evaluation results.

## How to Run the Application

To run the IdeaEvals application, follow these steps:

1.  **Prerequisites:**
    *   Ensure you have Python 3.9+ installed.
    *   `git` should be installed if you need to clone the repository.

2.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd IdeaEvals
    ```
    (Assuming you are already in the `IdeaEvals` directory)

3.  **Set up a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    ```

4.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

5.  **Install Dependencies:**
    Install all required Python packages using `pip` and the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

6.  **Configure Environment Variables:**
    The application likely uses environment variables for API keys (e.g., for LLMs) or other sensitive settings. Create a `.env` file in the project root (if one doesn't exist) and populate it with necessary variables. For example:
    ```
    OPENAI_API_KEY=your_openai_api_key
    GEMINI_API_KEY=your_gemini_api_key
    # Add other necessary environment variables here
    ```

7.  **Prepare Input Data:**
    Ensure your input data is correctly placed. For example, `data/ideas.xlsx` should contain the ideas to be processed, and any supplementary files should be in `data/additional_files/` within their respective idea ID folders.

8.  **Run the Pipeline:**
    Execute the main pipeline script.
    ```bash
    python run_pipeline.py
    ```

9.  **Deactivate Virtual Environment (when done):**
    ```bash
    deactivate
    ```

This will execute the entire idea evaluation pipeline, and the results will be generated according to the configuration.