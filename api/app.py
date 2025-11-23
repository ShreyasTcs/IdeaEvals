from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import threading
import time
import json
import os 
from pathlib import Path
import logging
import base64
import pandas as pd
import io
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock LLMProvider for demonstration purposes
class MockLLMProvider:
    def generate_content(self, prompt: str, **kwargs):
        logger.info(f"MockLLMProvider: Generating content for prompt (first 100 chars): {prompt[:100]}...")
        # Simulate LLM response
        time.sleep(0.5)
        return "Mock LLM Response"

    def generate_json(self, prompt: str, **kwargs):
        logger.info(f"MockLLMProvider: Generating JSON for prompt (first 100 chars): {prompt[:100]}...")
        # Simulate LLM JSON response
        time.sleep(0.5)
        return {"mock_key": "mock_value"}

    def generate_text(self, prompt: str) -> str:
        logger.info(f"MockLLMProvider: Generating text for prompt (first 100 chars): {prompt[:100]}...")
        time.sleep(1) # Simulate some delay
        if "NOVELTY" in prompt.upper():
            return "This rubric assesses the uniqueness and originality of the idea, its differentiation from existing solutions, and its potential to create new market categories or disrupt existing ones."
        elif "CLARITY" in prompt.upper():
            return "This rubric evaluates how clearly the idea is articulated, including its problem statement, target audience, value proposition, and overall understanding of the domain."
        elif "FEASIBILITY" in prompt.upper():
            return "This rubric examines the technical viability of the idea, the credibility of its approach, resource requirements, potential risks, and mitigation strategies."
        elif "LONG_TERM_VALUE" in prompt.upper():
            return "This rubric focuses on the sustainable impact and growth potential of the idea, including its business model, market strategy, scalability, and alignment with long-term trends."
        elif "SECURITY_COMPLIANCE" in prompt.upper():
            return "This rubric assesses the idea's adherence to security best practices, data privacy regulations, and relevant compliance standards, including measures for responsible AI."
        elif "EVIDENCE" in prompt.upper():
            return "This rubric evaluates the presence and quality of supporting evidence, such as prototypes, demos, benchmarks, user feedback, and comprehensive documentation."
        else:
            return f"A generated description for {prompt.split('Rubric Category: ')[1].split('\n')[0].strip() if 'Rubric Category: ' in prompt else 'this rubric'}."

    def count_tokens(self, text: str) -> int:
        return len(text.split()) # Simple token count


# Import IdeaProcessor (assuming it's in core.idea_processor)
# We need to adjust the import path based on the project structure
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core.idea_processor import IdeaProcessor
from llm.azure_openai_provider import AzureOpenAIProvider

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for evaluation states
evaluations = {} # {evaluation_id: {status: 'pending'|'processing'|'completed'|'failed', progress: {...}, results: {...}}}

def decode_base64_file(encoded_string: str) -> bytes:
    # Remove the data URL prefix (e.g., "data:text/csv;base64,")
    if ';base64,' in encoded_string:
        encoded_string = encoded_string.split(';base64,')[1]
    return base64.b64decode(encoded_string)

def parse_ideas_file(file_content: bytes, filename: str) -> list[dict]:
    df = None
    file_extension = Path(filename).suffix.lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(io.BytesIO(file_content))
    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Convert DataFrame to a list of dictionaries
    return df.to_dict(orient='records')

def run_evaluation_task(evaluation_id, hackathon_name, hackathon_description, rubrics, additional_files, ideas_file_base64, ideas_file_name):
    logger.info(f"Starting evaluation task for ID: {evaluation_id}")
    evaluations[evaluation_id] = {
        'status': 'processing',
        'total_ideas': 0,
        'processed_ideas': 0,
        'estimated_time_remaining': 'Calculating...', 
        'results': None,
        'error': None
    }

    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    config_dir = project_root / "config"
    run_pipeline_script = project_root / "run_pipeline.py"

    # Ensure data and config directories exist
    data_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    ideas_filepath = data_dir / "ideas.xlsx" # This will be overwritten by the uploaded file
    rubrics_filepath = config_dir / "rubrics.json" # This will be overwritten by the uploaded rubrics
    output_filepath = data_dir / f"evaluation_results_{evaluation_id}.json" # Unique output file

    try:
        # 1. Write ideas file
        if ideas_file_base64 and ideas_file_name:
            decoded_ideas_content = decode_base64_file(ideas_file_base64)
            with open(ideas_filepath, 'wb') as f:
                f.write(decoded_ideas_content)
            logger.info(f"Ideas file saved to {ideas_filepath}")
        else:
            raise ValueError("No ideas file provided for evaluation.")

        # 2. Write rubrics file
        with open(rubrics_filepath, 'w') as f:
            json.dump(rubrics, f, indent=2)
        logger.info(f"Rubrics saved to {rubrics_filepath}")

        # 3. Execute run_pipeline.py
        logger.info(f"Executing pipeline script: {run_pipeline_script}")
        command = [
            sys.executable,
            str(run_pipeline_script),
            '--ideas_filepath', str(ideas_filepath),
            '--rubrics_filepath', str(rubrics_filepath),
            '--output_filepath', str(output_filepath)
        ]
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8', # Explicitly set encoding to UTF-8
            check=True, # Raise an exception for non-zero exit codes
            cwd=project_root # Run from project root to ensure paths are correct
        )
        logger.info(f"Pipeline stdout:\n{process.stdout}")
        if process.stderr:
            logger.warning(f"Pipeline stderr:\n{process.stderr}")

        # 4. Read results from the generated JSON file
        if not output_filepath.exists():
            raise FileNotFoundError(f"Pipeline did not generate expected output file: {output_filepath}")
        
        with open(output_filepath, 'r') as f:
            results = json.load(f)
        logger.info(f"Results loaded from {output_filepath}")

        evaluations[evaluation_id]['status'] = 'completed'
        evaluations[evaluation_id]['results'] = results
        evaluations[evaluation_id]['total_ideas'] = len(results)
        evaluations[evaluation_id]['processed_ideas'] = len(results)
        evaluations[evaluation_id]['estimated_time_remaining'] = '0m 0s'
        logger.info(f"Evaluation task {evaluation_id} completed successfully.")

    except FileNotFoundError as e:
        logger.error(f"File error during evaluation task {evaluation_id}: {e}", exc_info=True)
        evaluations[evaluation_id]['status'] = 'failed'
        evaluations[evaluation_id]['error'] = str(e)
    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline script failed for evaluation task {evaluation_id}. Exit Code: {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}", exc_info=True)
        evaluations[evaluation_id]['status'] = 'failed'
        evaluations[evaluation_id]['error'] = f"Pipeline execution failed: {e.stderr}"
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from pipeline output for evaluation task {evaluation_id}: {e}", exc_info=True)
        evaluations[evaluation_id]['status'] = 'failed'
        evaluations[evaluation_id]['error'] = f"Error reading pipeline results: {e}"
    except Exception as e:
        logger.error(f"Unexpected error during evaluation task {evaluation_id}: {e}", exc_info=True)
        evaluations[evaluation_id]['status'] = 'failed'
        evaluations[evaluation_id]['error'] = str(e)
    finally:
        # Clean up temporary files (optional, but good practice)
        if ideas_filepath.exists():
            # ideas_filepath.unlink() # Keep for debugging for now
            pass
        if rubrics_filepath.exists():
            # rubrics_filepath.unlink() # Keep for debugging for now
            pass

@app.route('/evaluate', methods=['POST'])
def start_evaluation():
    data = request.get_json()
    hackathon_name = data.get('hackathonName')
    hackathon_description = data.get('hackathonDescription')
    rubrics = data.get('rubrics')
    additional_files = data.get('additionalFiles')
    ideas_file_base64 = data.get('ideasFile')
    ideas_file_name = data.get('ideasFileName')

    if not all([hackathon_name, rubrics, ideas_file_base64, ideas_file_name]):
        return jsonify({"message": "Missing required evaluation parameters"}), 400

    evaluation_id = str(uuid.uuid4())
    
    # Start the evaluation in a new thread
    thread = threading.Thread(target=run_evaluation_task, args=(evaluation_id, hackathon_name, hackathon_description, rubrics, additional_files, ideas_file_base64, ideas_file_name))
    thread.start()

    return jsonify({"evaluationId": evaluation_id}), 202 # 202 Accepted

@app.route('/evaluation/progress/<evaluation_id>', methods=['GET'])
def get_evaluation_progress(evaluation_id):
    evaluation = evaluations.get(evaluation_id)
    if not evaluation:
        return jsonify({"message": "Evaluation not found"}), 404
    
    # Return a copy to prevent external modification
    progress_data = {k: v for k, v in evaluation.items() if k != 'results'}
    return jsonify(progress_data), 200

@app.route('/evaluation/results/<evaluation_id>', methods=['GET'])
def get_evaluation_results(evaluation_id):
    evaluation = evaluations.get(evaluation_id)
    if not evaluation:
        return jsonify({"message": "Evaluation not found"}), 404
    
    if evaluation['status'] != 'completed':
        return jsonify({"message": "Evaluation not yet completed"}), 409 # 409 Conflict
    
    # Read results from the file
    results_file_path = Path(__file__).parent.parent / "data" / f"evaluation_results_{evaluation_id}.json"
    if not results_file_path.exists():
        return jsonify({"message": "Evaluation results file not found"}), 404
    
    try:
        with open(results_file_path, 'r') as f:
            results = json.load(f)
        return jsonify(results), 200
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from results file {results_file_path}: {e}", exc_info=True)
        return jsonify({"message": "Error decoding evaluation results"}), 500

@app.route('/api/hello')
def hello():
    return jsonify(message='Hello from the backend!')

@app.route('/generate-rubric-description', methods=['POST'])
def generate_rubric_description():
    data = request.get_json()
    rubric_name = data.get('rubricName')

    if not rubric_name:
        return jsonify({"message": "Missing rubricName parameter"}), 400

    try:
        azure_llm_provider = AzureOpenAIProvider()
        prompt_template_path = Path(__file__).parent.parent / "prompts" / "rubric_description_prompt.txt"
        with open(prompt_template_path, "r") as f:
            prompt_template = f.read()
        
        prompt = prompt_template.format(rubric_name=rubric_name)
        generated_description = azure_llm_provider.generate_text(prompt)

        if generated_description:
            return jsonify({"description": generated_description}), 200
        else:
            return jsonify({"message": "Failed to generate description from LLM"}), 500

    except Exception as e:
        logger.error(f"Error generating rubric description: {e}", exc_info=True)
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)