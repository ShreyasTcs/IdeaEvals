import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ADDITIONAL_FILES_DIR = DATA_DIR / "additional_files"
SCHEMA_FILE = BASE_DIR / "config" / "schema.json"

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'harikv@007',  # Change this
    'port': 5432
}

# Gemini API
GEMINI_API_KEY = "AIzaSyBG7cGklDEs-ta0fl_5FykWRgMwW1XVkv4"
GEMINI_MODEL = "gemini-2.5-pro"

# Processing settings
BATCH_SIZE = 8  # Number of ideas to process in parallel (idea-level parallelism)
MAX_FILE_WORKERS = 3  # ✅ NEW: Number of files to process in parallel per idea

MAX_RETRIES = 3
TIMEOUT_SECONDS = 120

# File settings
SUPPORTED_EXTENSIONS = ['.pdf', '.pptx', '.docx', '.mp4', '.mov', '.jpg', '.jpeg', '.png', '.webp']
MAX_FILE_SIZE_MB = 50

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "pipeline.log"
