# agent/guideline_manager.py
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION_START # For page numbering breaks
from docx.enum.style import WD_STYLE_TYPE # For potential style usage

# Define common constants (based on typical guidelines, adjust as needed from OCR text)
FONT_TIMES_NEW_ROMAN = "Times New Roman"
# COLOR_BLACK = RGBColor(0, 0, 0) # Example, if needed later

class GuidelineManager:
    """
    Stores and provides access to the formatting and content rules
    derived from the project guidelines document.

    Note: Rules are currently hardcoded based on common academic standards
    and the provided guideline structure. You MUST review your specific
    guidelines_ocr.txt/PDF and adjust these dictionaries meticulously.
    """

    def __init__(self, guideline_file_path: str = None):
        """
        Initializes the GuidelineManager.

        Args:
            guideline_file_path (str, optional): Path to the OCR text file.
                                                Currently not used for parsing,
                                                but kept for future potential use.
        """
        self.guideline_file_path = guideline_file_path
        # --- Define Rules Here ---
        # You MUST meticulously update these values based on your specific guidelines PDF/OCR
        self._rules = {
            "common": {
                "page_size": "A4", # Standard A4 size
                "figure_prefix": "Fig",
                "table_prefix": "Table",
                "reference_style": "IEEE", # As specified
            },
            "synopsis": {
                "page_limit_min": 6,
                "page_limit_max": 10, # Body pages
                "margins": { # Example values - CHECK YOUR PDF
                    "top": Inches(1.0),
                    "bottom": Inches(1.0),
                    "left": Inches(1.25),
                    "right": Inches(1.0),
                },
                "font_default": FONT_TIMES_NEW_ROMAN,
                "page_numbering": {
                    "format": "arabic", # Simple arabic numbers
                    "position": "bottom_center",
                    "start_page": 1,
                },
                "formatting_styles": {
                    "normal_text": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5, "align": WD_ALIGN_PARAGRAPH.JUSTIFY},
                    "heading1": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.LEFT, "space_before": Pt(12), "space_after": Pt(6)}, # Example Section Heading (1., 2.)
                    "title_main": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(18), "bold": True, "all_caps": True, "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_sub": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_info": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_supervisor": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.RIGHT},
                    "title_dept": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(16), "bold": True, "align": WD_ALIGN_PARAGRAPH.CENTER},
                    # Add other specific styles needed for Synopsis Title Page
                },
                "section_order": [ # Expected sections for the Synopsis body
                    "Introduction",
                    "Background and Literature Review",
                    "Problem Statement and Objectives",
                    "Methodology and Tools Used",
                    "Expected Results and Contribution",
                    "References" # Or maybe placed after contents page? Check guidelines
                ],
                 "title_page_layout": [ # Define the sequence and style for title page elements
                    # Style key refers to formatting_styles above
                    {"type": "logo", "optional": True}, # Placeholder for potential logo handling later
                    {"key": "project_title", "style": "title_main", "space_after": Pt(18)},
                    {"text": "A Project Synopsis Submitted for the Degree of", "style": "title_info"},
                    {"key": "course_code", "style": "title_info", "prefix": "Master of Computer Science (", "suffix": ")"}, # Check exact course name
                    {"text": "By", "style": "title_sub", "space_before": Pt(12), "space_after": Pt(6)},
                    {"key": "student_name", "style": "title_sub"},
                    {"key": "roll_number", "style": "title_sub", "prefix": "(Roll No.: ", "suffix": ")"},
                    {"text": "Under the Supervision of", "style": "title_supervisor", "space_before": Pt(36), "space_after": Pt(6)},
                    {"key": "supervisor_name", "style": "title_supervisor"},
                    {"key": "supervisor_designation", "style": "title_supervisor"},
                    {"key": "department", "style": "title_dept", "space_before": Pt(36), "space_after": Pt(6)},
                    {"key": "college", "style": "title_dept"},
                    {"key": "submission_month_year", "style": "title_info", "space_before": Pt(12)},
                ]
            },
            "report": {
                "page_limit_min": 40,
                "page_limit_max": 70, # Body pages (excluding front matter)
                "binding_margin": Inches(0.5), # Added to left margin
                "margins": { # Example values - CHECK YOUR PDF
                    "top": Inches(1.0),
                    "bottom": Inches(1.0),
                    "left": Inches(1.5), # Typical binding side
                    "right": Inches(1.0),
                },
                "font_default": FONT_TIMES_NEW_ROMAN,
                "page_numbering": {
                    "front_matter_format": "roman_lower", # i, ii, iii
                    "body_format": "arabic", # 1, 2, 3
                    "position": "bottom_center",
                    "start_page": 1, # Body starts at 1
                },
                "formatting_styles": {
                    # Base Styles
                    "normal_text": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5,
                                     "align": WD_ALIGN_PARAGRAPH.LEFT, # CHANGED from JUSTIFY
                                     "first_line_indent": Inches(0.5)},
                    "abstract": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5,
                                 "align": WD_ALIGN_PARAGRAPH.LEFT}, # CHANGED from JUSTIFY
                    "acknowledgement": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5,
                                        "align": WD_ALIGN_PARAGRAPH.LEFT}, # CHANGED from JUSTIFY
                    "list_entry": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5,
                                   "align": WD_ALIGN_PARAGRAPH.LEFT},
                    "caption": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(10), "line_spacing": 1.0,
                                "align": WD_ALIGN_PARAGRAPH.CENTER, # Captions often centered
                                "space_before": Pt(6), "space_after": Pt(12)},
                    "reference": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(10), "line_spacing": 1.0,
                                  "align": WD_ALIGN_PARAGRAPH.LEFT, "hanging_indent": Inches(0.5)},
                    # Declaration body can often remain justified if desired by guidelines
                    "declaration_body": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5,
                                         "align": WD_ALIGN_PARAGRAPH.JUSTIFY}, # Kept JUSTIFY (or change to LEFT)
                    # ADDED style for page numbers
                    "page_number": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(10)},

                    
                    # Headings (Check exact sizes/styles from PDF)
                    "heading_chapter": { # Level 1
                        "font": FONT_TIMES_NEW_ROMAN, "size": Pt(16),
                        "bold": True, "all_caps": True,
                        "align": WD_ALIGN_PARAGRAPH.CENTER,
                        "space_before": Pt(24), # Space before chapter title
                        "space_after": Pt(18),  # Space after chapter title
                        "keep_with_next": True, # Keep chapter title with first paragraph
                        "page_break_before": True # Start each chapter on a new page
                        },
                    "heading_section": { # Level 2
                        "font": FONT_TIMES_NEW_ROMAN, "size": Pt(14),
                        "bold": True, "all_caps": False, # Sections usually not all caps
                        "align": WD_ALIGN_PARAGRAPH.LEFT,
                        "space_before": Pt(12),
                        "space_after": Pt(6),
                        "keep_with_next": True
                        },
                    "heading_subsection": { # Level 3
                        "font": FONT_TIMES_NEW_ROMAN, "size": Pt(12),
                        "bold": True, "all_caps": False,
                        "align": WD_ALIGN_PARAGRAPH.LEFT,
                        "space_before": Pt(10),
                        "space_after": Pt(4),
                        "keep_with_next": True
                        },

                    # Title Page (Similar to Synopsis, may have slight variations)
                    "title_main": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(18), "bold": True, "all_caps": True, "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_sub": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_info": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "align": WD_ALIGN_PARAGRAPH.CENTER},
                    "title_supervisor": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "align": WD_ALIGN_PARAGRAPH.RIGHT},
                    "title_dept": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(16), "bold": True, "align": WD_ALIGN_PARAGRAPH.CENTER},

                    # Declaration Page
                    "declaration_heading": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(14), "bold": True, "underline": True, "align": WD_ALIGN_PARAGRAPH.CENTER, "space_after": Pt(18)},
                    "declaration_body": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "line_spacing": 1.5, "align": WD_ALIGN_PARAGRAPH.JUSTIFY},
                    "declaration_signature": {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12), "align": WD_ALIGN_PARAGRAPH.RIGHT, "space_before": Pt(36)},
                },
                # Define the sequence for front matter, body, back matter
                "structure": {
                    "front_matter": ["Title Page", "Declaration", "Acknowledgement", "Table of Contents", "List of Figures", "List of Tables", "List of Abbreviations", "Abstract"],
                    "body_chapters": [ # Typical chapters - adjust if needed
                        "Introduction", # Chapter 1
                        "Background and Literature Review", # Chapter 2
                        "System Design and Methodology", # Chapter 3
                        "Implementation and Results", # Chapter 4
                        "Conclusion and Future Scope" # Chapter 5
                    ],
                    "back_matter": ["References", "Appendices"]
                },
                "title_page_layout": [ # Similar to synopsis, adjust if needed
                     # Style key refers to formatting_styles above
                    {"type": "logo", "optional": True}, # Placeholder for logo handling
                    {"key": "project_title", "style": "title_main", "space_after": Pt(18)},
                    {"text": "A Project Report Submitted for the Degree of", "style": "title_info"},
                    {"key": "course_code", "style": "title_info", "prefix": "Master of Computer Science (", "suffix": ")"}, # Check exact course name
                    {"text": "By", "style": "title_sub", "space_before": Pt(12), "space_after": Pt(6)},
                    {"key": "student_name", "style": "title_sub"},
                    {"key": "roll_number", "style": "title_sub", "prefix": "(Roll No.: ", "suffix": ")"},
                    {"text": "Under the Supervision of", "style": "title_supervisor", "space_before": Pt(36), "space_after": Pt(6)},
                    {"key": "supervisor_name", "style": "title_supervisor"},
                    {"key": "supervisor_designation", "style": "title_supervisor"},
                    {"key": "department", "style": "title_dept", "space_before": Pt(36), "space_after": Pt(6)},
                    {"key": "college", "style": "title_dept"},
                    {"key": "submission_month_year", "style": "title_info", "space_before": Pt(12)},
                ],
                "declaration_text": """\
I hereby declare that the project work entitled "{project_title}" is an authentic record of my own work carried out under the supervision of {supervisor_name}.

I further declare that the work reported in this project has not been submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.

(Signature)

{student_name}
Roll No.: {roll_number}
Date: {submission_date} Place: Hisar""" # Placeholder for date
            }
        }
        self._load_rules_from_file() # Placeholder for potential future implementation

    def _load_rules_from_file(self):
        """
        Placeholder method to potentially load/override rules from the
        guideline OCR text file in the future. Requires sophisticated NLP/parsing.
        Currently does nothing.
        """
        if self.guideline_file_path:
            # In a future version, one might attempt to parse the text file here
            # using regex or NLP to find and extract specific rules,
            # then update the self._rules dictionary. This is complex.
            # print(f"Note: Parsing rules from {self.guideline_file_path} is not yet implemented.")
            pass


    def get_doc_rules(self, doc_type: str) -> dict:
        """Gets all rules for a specific document type ('synopsis' or 'report')."""
        if doc_type not in self._rules:
            raise ValueError(f"Unknown document type: {doc_type}")
        # Combine common rules with type-specific rules
        common = self._rules.get("common", {})
        specific = self._rules.get(doc_type, {})
        # Merge dictionaries (specific rules override common ones if keys conflict)
        return {**common, **specific}

    def get_formatting_rule(self, doc_type: str, style_key: str) -> dict:
        """Gets specific formatting style details for a given key."""
        doc_rules = self.get_doc_rules(doc_type)
        styles = doc_rules.get("formatting_styles", {})
        style = styles.get(style_key)
        if not style:
             print(f"Warning: Formatting style key '{style_key}' not found for doc_type '{doc_type}'. Using default.")
             # Return a basic default or raise an error
             return {"font": FONT_TIMES_NEW_ROMAN, "size": Pt(12)}
        return style

    def get_section_order(self, doc_type: str) -> list:
        """Gets the list of body sections/chapters in order."""
        doc_rules = self.get_doc_rules(doc_type)
        if doc_type == 'synopsis':
            return doc_rules.get("section_order", [])
        elif doc_type == 'report':
            # Report uses chapters, defined in structure
            structure = doc_rules.get("structure", {})
            return structure.get("body_chapters", [])
        return []

    def get_report_structure(self) -> dict:
        """Gets the overall structure definition for the final report."""
        report_rules = self.get_doc_rules("report")
        return report_rules.get("structure", {})


    def get_title_page_layout(self, doc_type: str) -> list:
        """Gets the layout definition for the title page."""
        doc_rules = self.get_doc_rules(doc_type)
        return doc_rules.get("title_page_layout", [])

    def get_declaration_text_template(self) -> str:
        """Gets the template string for the declaration page."""
        report_rules = self.get_doc_rules("report")
        return report_rules.get("declaration_text", "Declaration text not found.")

    def get_margins(self, doc_type: str) -> dict:
        """Gets the margin settings."""
        doc_rules = self.get_doc_rules(doc_type)
        return doc_rules.get("margins", {})

    def get_page_numbering_rules(self, doc_type: str) -> dict:
        """Gets page numbering rules."""
        doc_rules = self.get_doc_rules(doc_type)
        return doc_rules.get("page_numbering", {})

    # Add other getter methods as needed (e.g., get_page_limits)