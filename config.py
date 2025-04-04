
# --- Configuration settings for the Project Report Agent --- #

# Ollama Settings
OLLAMA_API_URL = 'http://192.168.0.193:11434/api/generate'
# Specify the model you have downloaded and want to use with Ollama
DEFAULT_OLLAMA_MODEL = 'gemma3:latest' # E.g., 'mistral', 'llama2', 'codellama'

# File Paths (relative to the project root)
GUIDELINES_FILE_PATH = 'data/guidelines_ocr.txt'
OUTPUT_DIR = 'output/'

# Input File Config
PROJECT_DATA_FILE_PATH = 'project_data.yaml'
# Key name within project_data.yaml that holds the logo path
LOGO_IMAGE_PATH_KEY = 'logo_image_path'

# Document Types (used internally)
DOC_SYNOPSIS = 'synopsis'
DOC_REPORT = 'report'

# ... other settings ...