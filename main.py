# main.py (Final Version)
import config
from agent.report_builder import ReportBuilder # Import ReportBuilder
from agent.guideline_manager import GuidelineManager
from agent.ollama_client import OllamaClient
from agent.content_generator import ContentGenerator
from agent.document_formatter import DocumentFormatter
from agent.input_parser import InputParser
import sys
from pathlib import Path # For dummy image creation if needed

# --- Helper to create a dummy image file for testing ---
# (Keep this if you want the optional figure generation in ReportBuilder to work)
def create_dummy_image(filepath="data/sample_figure.png"):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        try:
            from PIL import Image, ImageDraw # Needs Pillow: pip install Pillow
            img = Image.new('RGB', (200, 100), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10,10), "Sample Figure", fill=(255,255,0))
            img.save(path)
            print(f"    Created dummy image: {path}")
            return str(path)
        except ImportError:
            print("    Pillow not installed. pip install Pillow")
            path.touch() # Create empty file as fallback
            print(f"    Created empty placeholder file: {path}")
            return str(path)
        except Exception as e: print(f"    Error creating dummy image: {e}"); return None
    return str(path)

def run_agent():
    print('\n--- AI Project Report Agent ---')

    # 1. Load Configuration & Guidelines
    print('[1] Loading guidelines...')
    try:
        guideline_mgr = GuidelineManager(config.GUIDELINES_FILE_PATH)
        print('    GuidelineManager initialized.')
    except Exception as e:
        print(f"    ERROR: Failed to initialize GuidelineManager: {e}"); sys.exit(1)

    # 2. Load Project Data from Input File
    print(f'[2] Loading project data from {config.PROJECT_DATA_FILE_PATH}...')
    try:
        input_parser = InputParser(config.PROJECT_DATA_FILE_PATH)
        project_data = input_parser.load_and_validate()
        print('    Project data loaded successfully.')
    except FileNotFoundError:
        print(f'    ERROR: Input file not found: {config.PROJECT_DATA_FILE_PATH}'); sys.exit(1)
    except Exception as e:
        print(f'    ERROR: Failed to load or parse input file: {e}'); sys.exit(1)

    # 3. Initialize Core Components
    print('[3] Initializing agent components...')
    try:
        ollama_client = OllamaClient(model_name=config.DEFAULT_OLLAMA_MODEL, api_url=config.OLLAMA_API_URL)
        content_gen = ContentGenerator(ollama_client, guideline_mgr)
        doc_formatter = DocumentFormatter(guideline_mgr)
        # Initialize ReportBuilder with all components
        report_builder = ReportBuilder(
            guideline_manager=guideline_mgr,
            content_generator=content_gen,
            document_formatter=doc_formatter,
            output_dir=config.OUTPUT_DIR
        )
        print('    Core components initialized.')
    except Exception as e:
         print(f"    ERROR: Failed to initialize agent components: {e}"); sys.exit(1)

    # --- Create dummy image if needed by ReportBuilder examples ---
    create_dummy_image()

    # 4. Choose Document Type
    doc_type = ''
    while doc_type not in [config.DOC_SYNOPSIS, config.DOC_REPORT]:
        doc_choice = input(f'>>> Generate [{config.DOC_SYNOPSIS}] or [{config.DOC_REPORT}]? ').lower().strip()
        if doc_choice == config.DOC_SYNOPSIS: doc_type = config.DOC_SYNOPSIS
        elif doc_choice == config.DOC_REPORT: doc_type = config.DOC_REPORT
    print(f'    Selected document type: {doc_type}')

    # 5. Build the Document (Remove the old test block)
    print(f'\n[4] Starting main build process for {doc_type.upper()}...')
    try:
        # Call the main build method
        report_builder.build(doc_type, project_data)
        print(f"\n--- Agent Finished: Check the '{config.OUTPUT_DIR}' folder. ---")
    except Exception as e:
         print(f"\n--- FATAL ERROR DURING BUILD PROCESS ---")
         import traceback
         traceback.print_exc()
         print("-----------------------------------------")

if __name__ == '__main__':
    run_agent()