# agent/report_builder.py
import os
from pathlib import Path
import config # For DOC_SYNOPSIS, DOC_REPORT constants etc.
from .guideline_manager import GuidelineManager
from .content_generator import ContentGenerator
from .document_formatter import DocumentFormatter
# No need for InputParser here, data comes pre-parsed

class ReportBuilder:
    """
    Orchestrates the generation of project reports or synopses by coordinating
    GuidelineManager, ContentGenerator, and DocumentFormatter.
    """

    # Mapping from guideline section names (expected from GuidelineManager)
    # to the corresponding ContentGenerator methods.
    # Keys should match the strings returned by guideline_mgr.get_section_order()
    # or guideline_mgr.get_report_structure()['body_chapters']
    SECTION_GENERATOR_MAP = {
        # Synopsis Sections (keys might need adjustment based on GuidelineManager exact output)
        "Introduction": "generate_introduction",
        "Background and Literature Review": "generate_literature_review",
        "Problem Statement and Objectives": "generate_problem_and_objectives",
        "Methodology and Tools Used": "generate_methodology",
        "Expected Results and Contribution": "generate_results",
        # Report Chapters (keys might need adjustment)
        # "Introduction": "generate_introduction", # Covered above
        # "Background and Literature Review": "generate_literature_review", # Covered above
        "System Design and Methodology": "generate_methodology",
        "Implementation and Results": "generate_results",
        "Conclusion and Future Scope": "generate_conclusion_future_scope",
        # Common sections (handled separately or via specific logic)
        # "References": None, # Handle manually
        # "Appendices": None, # Handle manually
        # "Acknowledgement": "generate_acknowledgement", # Handled explicitly
        # "Abstract": "generate_abstract", # Handled explicitly
    }


    def __init__(self, guideline_manager: GuidelineManager,
                 content_generator: ContentGenerator,
                 document_formatter: DocumentFormatter,
                 output_dir: str = config.OUTPUT_DIR):
        """
        Initializes the ReportBuilder.

        Args:
            guideline_manager (GuidelineManager): Provides rules and structure.
            content_generator (ContentGenerator): Generates text content.
            document_formatter (DocumentFormatter): Formats and builds the DOCX.
            output_dir (str): Directory to save the final documents.
        """
        self.guideline_mgr = guideline_manager
        self.content_gen = content_generator
        self.formatter = document_formatter
        self.output_dir = Path(output_dir)
        print("    ReportBuilder initialized.")

    def build(self, doc_type: str, project_data: dict):
        """
        Builds the specified document type (synopsis or report).

        Args:
            doc_type (str): config.DOC_SYNOPSIS or config.DOC_REPORT.
            project_data (dict): Parsed data from the input YAML file.
        """
        print(f"\n--- Starting build process for: {doc_type.upper()} ---")
        if doc_type not in [config.DOC_SYNOPSIS, config.DOC_REPORT]:
            print(f"    ERROR: Invalid document type '{doc_type}'. Cannot build.")
            return

        # --- 1. Preparation ---
        # Extract key info for filename etc.
        roll_number = project_data.get('roll_number', 'UnknownRollNo')
        print(f"    Project Title: {project_data.get('project_title', 'N/A')}")
        print(f"    Student Roll No: {roll_number}")

        # Create the base document (resets formatter tracking, applies margins)
        self.formatter.create_document(doc_type)

        # --- 2. Build Front Matter ---
        print("\n    [Phase 1: Building Front Matter]")
        self.formatter.add_title_page(doc_type, project_data)

        if doc_type == config.DOC_REPORT:
            self.formatter.add_declaration(project_data)

            # Generate and add Acknowledgement & Abstract
            ack_text = self.content_gen.generate_acknowledgement(project_data)
            self.formatter.add_acknowledgement(ack_text, doc_type)

            abs_text = self.content_gen.generate_abstract(project_data)
            self.formatter.add_abstract(abs_text, doc_type)

            # Insert Placeholders for dynamic lists
            self.formatter.insert_toc_placeholder(doc_type)
            self.formatter.insert_lof_placeholder(doc_type)
            self.formatter.insert_lot_placeholder(doc_type)
            # self.formatter.insert_loa_placeholder(doc_type) # If implementing List of Abbreviations

            # *** CRITICAL STEP for Page Numbering ***
            # Add a section break after the front matter (before Chapter 1)
            # This allows restarting page numbering with Arabic numerals.
            print("    Adding Section Break between Front Matter and Body...")
            self.formatter.add_section_break()

        # --- 3. Build Body Content ---
        print("\n    [Phase 2: Building Body Content]")
        body_sections = []
        if doc_type == config.DOC_REPORT:
            structure = self.guideline_mgr.get_report_structure()
            body_sections = structure.get('body_chapters', [])
        elif doc_type == config.DOC_SYNOPSIS:
            body_sections = self.guideline_mgr.get_section_order(doc_type)
             # Filter out non-body sections like 'References' if included in synopsis order
            body_sections = [s for s in body_sections if s.lower() != 'references']

        if not body_sections:
             print("    Warning: No body sections/chapters defined in GuidelineManager. Skipping body content.")
        else:
            print(f"    Processing body sections: {body_sections}")
            for section_name in body_sections:
                print(f"\n    Processing Section/Chapter: '{section_name}'")
                # Determine heading level (1 for chapters/main synopsis sections)
                level = 1

                # Add the heading using the formatter
                self.formatter.add_heading(section_name, level, doc_type)

                # Find the corresponding generator method name
                generator_method_name = self.SECTION_GENERATOR_MAP.get(section_name)

                if generator_method_name and hasattr(self.content_gen, generator_method_name):
                    # Get the generator method
                    generator_func = getattr(self.content_gen, generator_method_name)
                    # Call the generator method
                    section_content = generator_func(doc_type, project_data)
                else:
                    print(f"      Warning: No specific generator method found for '{section_name}'. Using generic fallback.")
                    # Use a generic generator call or provide placeholder text
                    section_content = self.content_gen.generate_section(section_name, doc_type, project_data)
                    if not section_content or "[Content" in section_content : # Check if fallback also failed
                         section_content = f"[Placeholder content for {section_name}. Generation failed or method not mapped.]"


                # Add the generated content to the document
                # Use 'normal_text' style defined in GuidelineManager
                self.formatter.add_formatted_paragraph(section_content, 'normal_text', doc_type)

                # --- Optional: Add Sample Figure/Table based on section ---
                # This is basic, could be driven by project_data hints
                if doc_type == config.DOC_REPORT:
                    if "methodology" in section_name.lower():
                         # Example: Add a figure in the methodology chapter
                         sample_img = "data/sample_figure.png" # Assumes dummy image exists
                         if Path(sample_img).exists():
                              self.formatter.add_figure(sample_img, f"Illustrative diagram for {section_name}.", doc_type)
                    elif "results" in section_name.lower():
                         # Example: Add a table in the results chapter
                         sample_data = [['Metric', 'Value'], ['Accuracy', '90%'], ['Speed', 'Fast']]
                         self.formatter.add_table(sample_data, f"Summary of key results for {section_name}.", doc_type)

        # --- 4. Build Back Matter ---
        print("\n    [Phase 3: Building Back Matter]")
        # Add References section heading
        ref_heading = "REFERENCES" if doc_type == config.DOC_REPORT else "References"
        self.formatter.add_heading(ref_heading, level=1, doc_type=doc_type) # Treat as Level 1 style/numbering? Check guidelines
        # Add placeholder text for references - Generation/formatting is complex
        self.formatter.add_formatted_paragraph(
            "[References list should be added here according to IEEE format as per guidelines.]",
            'normal_text', # Or maybe a specific 'reference_placeholder' style
            doc_type
        )

        if doc_type == config.DOC_REPORT:
            # Add Appendices section heading
            self.formatter.add_heading("APPENDICES", level=1, doc_type=doc_type) # Treat as Level 1 style?
            # Add placeholder text
            self.formatter.add_formatted_paragraph(
                "[Include any appendices here, such as source code snippets (if allowed/required), complex diagrams, or detailed data tables.]",
                'normal_text',
                doc_type
            )

        # --- 5. Finalize and Save ---
        print("\n    [Phase 4: Finalizing Document]")
        # Generate TOC, LoF, LoT; Apply Page Numbering
        self.formatter.finalize_document()

        # Construct filename
        filename_base = f"{doc_type.capitalize()}_{roll_number}"
        filename = self.output_dir / f"{filename_base}.docx"

        print(f"\n    Attempting to save final document to: {filename}")
        self.formatter.save_document(str(filename))

        print(f"\n--- Build process finished for: {doc_type.upper()} ---")