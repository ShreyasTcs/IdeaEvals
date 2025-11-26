# Modular Hackathon Evaluation Pipeline

This project provides a comprehensive system for evaluating hackathon ideas using Large Language Models (LLMs). It features a web-based frontend for setting up evaluations, a Flask backend to manage the processing, and a powerful Python pipeline for concurrent idea evaluation.

## Features

- **Web Interface**: A React-based frontend for easy setup of hackathons, rubrics, and idea submissions.
- **Real-time Progress**: Monitor the evaluation process in real-time.
- **Modular Backend**: A Flask API to handle evaluation requests and serve results.
- **Concurrent Processing**: The core pipeline processes multiple ideas in parallel for efficiency.
- **LLM Integration**: Supports multiple LLM providers (e.g., Gemini, Azure OpenAI) for evaluation.
- **Database Storage**: Stores all evaluation results in a PostgreSQL database for persistence and analysis.
- **Extensible Schema**: A well-defined database schema to store hackathons, submissions, rubrics, and results.

## System Architecture

The application is divided into three main components:

1.  **Frontend**: A React single-page application (`/frontend`) that allows users to:
    - Create a new hackathon evaluation.
    - Define custom rubrics for scoring.
    - Upload a file with the ideas to be evaluated.
    - View the real-time progress of the evaluation.
    - See the final results in a dashboard.

2.  **Backend API**: A Flask server (`/api/app.py`) that acts as the bridge between the frontend and the processing pipeline. It exposes endpoints to:
    - Start a new evaluation.
    - Provide real-time progress updates.
    - Serve the final evaluation results.

3.  **Evaluation Pipeline**: The core logic of the application (`/run_pipeline.py`). This script is responsible for:
    - Loading ideas and rubrics.
    - Interacting with the configured LLM to evaluate each idea against the rubrics.
    - Storing the results in a JSON file and a PostgreSQL database.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js and npm
- PostgreSQL server

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Configure Environment Variables

Create a `.env` file in the project root by copying the example file:

```bash
cp .env.example .env
```

Now, edit the `.env` file with your specific configurations:

```env
# Gemini API
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Azure OpenAI
AZURE_OPENAI_DEPLOYMENT="gpt-4.1"
AZURE_OPENAI_MODEL="gpt-4.1"
AZURE_OPENAI_API_VERSION="2025-01-01-preview"
AZURE_OPENAI_ENDPOINT="https://YOUR_ENDPOINT.openai.azure.com/"
AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_KEY"

# PostgreSQL Database
DB_HOST="localhost"
DB_DATABASE="postgres"
DB_USER="postgres"
DB_PASSWORD="your_password"
DB_PORT="5432"
```

### 3. Backend Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
```

### 4. Frontend Setup

Navigate to the frontend directory and install npm packages:

```bash
cd frontend
npm install
```

### 5. Running the Application

1.  **Start the Backend API**:

    ```bash
    python api/app.py
    ```

    The Flask server will start on `http://localhost:5000`.

2.  **Start the Frontend**:

    In a new terminal, navigate to the `/frontend` directory and run:

    ```bash
    npm start
    ```

    The React development server will start, and the application will open in your browser at `http://localhost:3000`.

## File Structure Overview

```
/
├── api/                    # Flask backend API
│   ├── app.py              # Main API file with endpoints
│   └── requirements.txt    # API-specific Python dependencies
├── app_io/                 # Input/Output helpers for the pipeline
├── config/                 # Project configuration
│   └── config.py           # Loads configuration from .env
├── core/                   # Core evaluation logic
│   └── idea_processor.py   # Processes a single idea
├── data/                   # Data files (e.g., uploaded ideas, results)
├── frontend/               # React frontend application
├── llm/                    # LLM provider integrations
├── prompts/                # Prompts used for the LLMs
├── utils/                  # Utility scripts
│   └── db_helper.py        # Database connection and operations
├── .env.example            # Example environment file
├── requirements.txt        # Core Python dependencies
├── run_pipeline.py         # Main script for the evaluation pipeline
└── tasklist.md             # Project tasks
```

## How to Run the Evaluation Pipeline Standalone

You can also run the evaluation pipeline directly from the command line. This is useful for testing or batch processing.

```bash
python run_pipeline.py --ideas_filepath "path/to/your/ideas.xlsx" --rubrics_filepath "path/to/your/rubrics.json" --output_filepath "path/to/your/results.json" --hackathon_name "My Hackathon"
```
