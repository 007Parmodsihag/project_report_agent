# agent/document_formatter.py
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION_START, WD_HEADER_FOOTER
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml # Import parse_xml for footer manipulation

from pathlib import Path
import os

from .guideline_manager import GuidelineManager # Assuming importable

# --- Placeholder Constants ---
TOC_PLACEHOLDER = "[---TABLE_OF_CONTENTS---]"
LOF_PLACEHOLDER = "[---LIST_OF_FIGURES---]"
LOT_PLACEHOLDER = "[---LIST_OF_TABLES---]"

COLOR_BLACK = RGBColor(0, 0, 0)

class DocumentFormatter:
    """
    Handles the creation, formatting, and finalization of the .docx document
    using python-docx, based on rules provided by GuidelineManager.
    Focus on correct Page Numbering (Roman/Arabic, no number on title)
    and detailed TOC generation.
    """
    def __init__(self, guideline_manager: GuidelineManager):
        self.guideline_mgr = guideline_manager
        self.doc = None
        self.current_section = None
        self.headings = []
        self.figures = []
        self.tables = []
        self.chapter_num = 0
        self.section_num = 0
        self.subsection_num = 0
        self.figure_num_in_chapter = 0
        self.table_num_in_chapter = 0
        self.current_chapter_number = 0
        self.placeholder_paragraphs = {}
        self.front_matter_section_index = 0 # Section 0: Title page
        # Section 1 up to body_section_index-1: Rest of front matter
        self.body_section_index = -1 # Index where main body (Arabic numbering) starts

    def _reset_tracking(self):
        print("    Resetting document tracking lists and counters.")
        # ... (reset lists and counters as before) ...
        self.headings = []
        self.figures = []
        self.tables = []
        self.chapter_num = 0; self.section_num = 0; self.subsection_num = 0
        self.figure_num_in_chapter = 0; self.table_num_in_chapter = 0
        self.current_chapter_number = 0
        self.placeholder_paragraphs = {}
        self.front_matter_section_index = 0
        self.body_section_index = -1

    def create_document(self, doc_type: str):
        self._reset_tracking()
        self.doc = Document()
        self.current_section = self.doc.sections[0]
        self.front_matter_section_index = 0 # Title page section
        self.current_section.page_width = Cm(21.0)
        self.current_section.page_height = Cm(29.7)
        print(f"    Document created. Page size set to A4. Tracking reset.")
        self.apply_margins(doc_type)
        return self.doc

    def apply_margins(self, doc_type: str):
        # ... (Apply margins as before) ...
        margins = self.guideline_mgr.get_margins(doc_type)
        if not margins: print(f"Warning: Margin rules not found for {doc_type}."); return
        try:
            section = self.doc.sections[-1]
            section.top_margin = margins.get('top', Inches(1.0)); section.bottom_margin = margins.get('bottom', Inches(1.0))
            section.left_margin = margins.get('left', Inches(1.25)); section.right_margin = margins.get('right', Inches(1.0))
            print(f"    Margins applied to Section {len(self.doc.sections)-1}: T={section.top_margin.inches:.2f}\", B={section.bottom_margin.inches:.2f}\", L={section.left_margin.inches:.2f}\", R={section.right_margin.inches:.2f}\"")
        except Exception as e: print(f"    Error applying margins: {e}")

    def _apply_paragraph_format(self, paragraph, style_key: str, doc_type: str):
        # ... (Apply paragraph formatting as before) ...
        style_rules = self.guideline_mgr.get_formatting_rule(doc_type, style_key)
        # (Apply basic default if style_rules is None - code omitted for brevity)
        if not style_rules: print(f"Warning: Style rule '{style_key}' not found."); return # Simplified

        p_format = paragraph.paragraph_format
        # (Apply align, spacing, indent, pagination - code omitted for brevity)
        if 'align' in style_rules: p_format.alignment = style_rules['align']
        if 'line_spacing' in style_rules: p_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE; p_format.line_spacing = style_rules['line_spacing']
        p_format.space_before = style_rules.get('space_before', Pt(0)); p_format.space_after = style_rules.get('space_after', Pt(0))
        p_format.first_line_indent = style_rules.get('first_line_indent', None); p_format.left_indent = style_rules.get('left_indent', None)
        p_format.right_indent = style_rules.get('right_indent', None); p_format.hanging_indent = style_rules.get('hanging_indent', None)
        p_format.keep_together = style_rules.get('keep_together', False); p_format.keep_with_next = style_rules.get('keep_with_next', False)
        p_format.page_break_before = style_rules.get('page_break_before', False); p_format.widow_control = style_rules.get('widow_control', True)

        base_font_name = style_rules.get('font', 'Times New Roman'); base_font_size = style_rules.get('size', Pt(12))
        is_bold = style_rules.get('bold', False); is_italic = style_rules.get('italic', False)
        is_underline = style_rules.get('underline', False); is_all_caps = style_rules.get('all_caps', False)
        font_color = style_rules.get('color', COLOR_BLACK)

        for run in paragraph.runs:
            font = run.font
            # (Apply font settings - code omitted for brevity)
            font.name = base_font_name; font.size = base_font_size; font.bold = is_bold; font.italic = is_italic
            font.underline = is_underline; font.all_caps = is_all_caps; font.color.rgb = font_color

    def add_formatted_paragraph(self, text: str, style_key: str, doc_type: str):
        # ... (Add formatted paragraph as before) ...
        if text is None: text = ""
        p = self.doc.add_paragraph(str(text))
        self._apply_paragraph_format(p, style_key, doc_type)
        return p

    def add_page_break(self): self.doc.add_page_break()

    def add_section_break(self, break_type=WD_SECTION_START.NEW_PAGE):
        # ... (Add section break and update body_section_index as before) ...
        self.doc.add_section(break_type)
        self.current_section = self.doc.sections[-1]
        print(f"    Added Section Break. Document now has {len(self.doc.sections)} sections.")
        self.apply_margins('report')
        if self.body_section_index == -1 and len(self.doc.sections) > 1:
             self.body_section_index = len(self.doc.sections) - 1
             print(f"    Body Section index set to: {self.body_section_index}")

    # --- Front Matter Methods ---
    def add_title_page(self, doc_type: str, project_data: dict):
        # ... (Add title page as before, ensuring correct supervisor designation) ...
        print(f"Adding Title Page ({doc_type})..."); layout = self.guideline_mgr.get_title_page_layout(doc_type)
        if not layout: print("Warning: Title page layout not found."); return
        # (Logo handling code omitted for brevity) ...
        for item in layout:
             if item.get("type") == "logo": continue # Skip logo if already handled
             style_key = item.get("style", "normal_text")
             text_to_add = item.get("text", "")
             if not text_to_add and "key" in item:
                  data_key = item["key"]
                  # Ensure correct designation is pulled
                  text_to_add = str(project_data.get(data_key, f"[{data_key}]"))
             final_text = f"{item.get('prefix', '')}{text_to_add}{item.get('suffix', '')}"
             p = self.add_formatted_paragraph(final_text, style_key, doc_type)
             if p:
                 if "space_before" in item: p.paragraph_format.space_before = item["space_before"]
                 if "space_after" in item: p.paragraph_format.space_after = item["space_after"]
        self.add_page_break(); print("      Title Page added.")

    def add_declaration(self, project_data: dict):
        # ... (Add declaration as before) ...
        print("Adding Declaration Page..."); doc_type = "report"; template = self.guideline_mgr.get_declaration_text_template()
        if not template or template == "Declaration text not found.": print("Warning: Declaration template not found."); return
        self.add_formatted_paragraph("DECLARATION", "declaration_heading", doc_type)
        try: # (Format and add text - code omitted for brevity)
             format_data = {k: project_data.get(k, f'[{k}]') for k in ['project_title', 'supervisor_name', 'student_name', 'roll_number']}
             format_data['submission_date'] = project_data.get('submission_month_year', '[Date]')
             declaration_body_text = template.format(**format_data)
             self.add_formatted_paragraph(declaration_body_text, "declaration_body", doc_type)
        except Exception as e: print(f"Error formatting declaration: {e}"); self.add_formatted_paragraph(template, "declaration_body", doc_type)
        self.add_page_break(); print("      Declaration Page added.")

    def add_acknowledgement(self, text: str, doc_type="report"):
        # ... (Add acknowledgement as before) ...
        print("Adding Acknowledgement Page..."); self.add_formatted_paragraph("ACKNOWLEDGEMENT", "heading_list_toc", doc_type)
        self.add_formatted_paragraph(text or "[Acknowledgement text not generated]", "acknowledgement", doc_type); self.add_page_break(); print("      Acknowledgement Page added.")

    def add_abstract(self, text: str, doc_type="report"):
        # ... (Add abstract as before) ...
        print("Adding Abstract Page..."); self.add_formatted_paragraph("ABSTRACT", "heading_list_toc", doc_type)
        self.add_formatted_paragraph(text or "[Abstract text not generated]", "abstract", doc_type); self.add_page_break(); print("      Abstract Page added.")

    # --- Placeholder Insertion ---
    def _insert_placeholder(self, placeholder_text: str, heading_text: str, heading_style: str, doc_type: str):
        # ... (Insert placeholder as before) ...
        print(f"    Inserting Placeholder for: {heading_text}")
        self.add_formatted_paragraph(heading_text, heading_style, doc_type)
        p = self.add_formatted_paragraph(placeholder_text, "normal_text", doc_type)
        self.placeholder_paragraphs[placeholder_text] = p
        self.add_page_break()

    def insert_toc_placeholder(self, doc_type="report"): self._insert_placeholder(TOC_PLACEHOLDER, "Table of Contents", "heading_list_toc", doc_type)
    def insert_lof_placeholder(self, doc_type="report"): self._insert_placeholder(LOF_PLACEHOLDER, "List of Figures", "heading_list_toc", doc_type)
    def insert_lot_placeholder(self, doc_type="report"): self._insert_placeholder(LOT_PLACEHOLDER, "List of Tables", "heading_list_toc", doc_type)

    # --- Body Content Methods ---
    def add_heading(self, text: str, level: int, doc_type: str):
        # ... (Add heading and track as before) ...
        if not text: return
        number_str, style_key, heading_text_final = "", "", text; is_numbered = False
        # (Logic for numbering/styling based on level/doc_type omitted for brevity - remains same)
        if doc_type == 'report':
            if level == 1: # Chapter
                self.chapter_num += 1; self.section_num, self.subsection_num = 0, 0
                self.figure_num_in_chapter, self.table_num_in_chapter = 0, 0
                self.current_chapter_number = self.chapter_num
                style_key = "heading_chapter"; number_str = f"{self.chapter_num}"
                heading_text_final = f"CHAPTER {number_str}: {text.upper()}"; is_numbered = True
            elif level == 2 and self.chapter_num > 0: # Section
                self.section_num += 1; self.subsection_num = 0
                style_key = "heading_section"; number_str = f"{self.chapter_num}.{self.section_num}"
                heading_text_final = f"{number_str} {text}"; is_numbered = True
            elif level == 3 and self.section_num > 0: # Subsection
                self.subsection_num += 1
                style_key = "heading_subsection"; number_str = f"{self.chapter_num}.{self.section_num}.{self.subsection_num}"
                heading_text_final = f"{number_str} {text}"; is_numbered = True
            else: # Fallback
                 print(f"Warning: Cannot correctly number heading L{level} ('{text}'). Adding unnumbered.")
                 style_key = "heading_subsection" if level >= 3 else ("heading_section" if level == 2 else "heading_chapter")
        elif doc_type == 'synopsis': # Synopsis
            if level == 1: # Synopsis Level 1
                 self.chapter_num += 1; style_key = "heading1"
                 number_str = f"{self.chapter_num}."; heading_text_final = f"{number_str} {text}"; is_numbered = True
            else: print(f"Warning: L{level} heading not standard for Synopsis ('{text}')."); style_key = "normal_text"

        print(f"    Adding Heading (L{level}, Num:{number_str or 'N/A'}, Style:{style_key}): {text}")
        p = self.add_formatted_paragraph(heading_text_final, style_key, doc_type)
        if p and is_numbered and style_key != "normal_text":
            self.headings.append({"level": level, "text": heading_text_final, "number": number_str, "paragraph": p})


    def add_figure(self, image_path_str: str, caption_text: str, doc_type="report"):
        # ... (Add figure and track as before) ...
        print(f"Adding Figure: {caption_text[:30]}..."); # (Error checking, numbering, prefix logic omitted for brevity)
        self.figure_num_in_chapter += 1
        figure_number_str = f"{self.current_chapter_number}.{self.figure_num_in_chapter}" if self.current_chapter_number > 0 else f"{self.figure_num_in_chapter}"
        figure_prefix = self.guideline_mgr.get_doc_rules(doc_type).get("figure_prefix", "Fig")
        full_caption = f"{figure_prefix} {figure_number_str}: {caption_text}"
        # (Image insertion logic omitted for brevity)
        caption_paragraph = self.add_formatted_paragraph(full_caption, "caption", doc_type)
        if caption_paragraph: self.figures.append({"number": figure_number_str, "caption": caption_text, "full_caption": full_caption, "paragraph": caption_paragraph}); print(f"      Figure {figure_number_str} added and tracked.")


    def add_table(self, data: list, caption_text: str, doc_type="report", header=True):
        # ... (Add table and track as before) ...
        print(f"Adding Table: {caption_text[:30]}..."); # (Error checking, numbering, prefix logic omitted for brevity)
        self.table_num_in_chapter += 1
        table_number_str = f"{self.current_chapter_number}.{self.table_num_in_chapter}" if self.current_chapter_number > 0 else f"{self.table_num_in_chapter}"
        table_prefix = self.guideline_mgr.get_doc_rules(doc_type).get("table_prefix", "Table")
        full_caption = f"{table_prefix} {table_number_str}: {caption_text}"
        caption_paragraph = self.add_formatted_paragraph(full_caption, "caption", doc_type)
        # (Table creation logic omitted for brevity)
        if caption_paragraph: self.tables.append({"number": table_number_str, "caption": caption_text, "full_caption": full_caption, "paragraph": caption_paragraph}); print(f"      Table {table_number_str} added and tracked.")

    # --- Page Numbering (REVISED)---

    def _add_page_number_field(self, run, style='arabic'):
        """Helper to add PAGE field using Oxml with format switch."""
        fldChar_begin = OxmlElement('w:fldChar'); fldChar_begin.set(qn('w:fldCharType'), 'begin')
        fldChar_instr = OxmlElement('w:instrText')
        format_switch = ""
        # Use standard Word field code switches
        if style == 'roman_lower': format_switch = r'\* lowerroman'
        elif style == 'roman_upper': format_switch = r'\* upperroman'
        # Arabic (decimal) is the default, no switch needed
        fldChar_instr.text = f' PAGE {format_switch} '
        fldChar_sep = OxmlElement('w:fldChar'); fldChar_sep.set(qn('w:fldCharType'), 'separate')
        fldChar_end = OxmlElement('w:fldChar'); fldChar_end.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar_begin); run._r.append(fldChar_instr); run._r.append(fldChar_sep); run._r.append(fldChar_end)

    def apply_page_numbering(self):
        """Applies page numbering: No number on title, Roman for front matter, Arabic for body."""
        print("    Applying Page Numbering...")
        if self.body_section_index == -1:
             print("      Warning: Body section index not set. Assuming Section 1 is body start."); self.body_section_index = 1
        num_rules = self.guideline_mgr.get_page_numbering_rules('report')
        front_format = num_rules.get('front_matter_format', 'roman_lower'); body_format = num_rules.get('body_format', 'arabic')
        position = num_rules.get('position', 'bottom_center')

        try:
            for i, section in enumerate(self.doc.sections):
                # --- Control Footer Linking ---
                # Section 0 (Title): Should have its own footer (empty)
                # Section 1 (Declaration etc.): Start Roman nums, don't link to Section 0
                # Subsequent Front Matter: Link footer to Section 1
                # Body Section: Start Arabic nums, don't link to front matter footer
                # Subsequent Body Sections: Link footer to first body section footer
                section.different_first_page_header_footer = False # Ensure consistent footer within section

                footer = section.footer
                if not footer.paragraphs: footer.add_paragraph()
                footer_para = footer.paragraphs[0]; footer_para.clear()
                footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                if i == self.front_matter_section_index: # Section 0: Title Page
                    print(f"      Section {i} (Title Page): Clearing footer (no page number).")
                    # Footer is already cleared, just ensure it's not linked if needed
                    footer.is_linked_to_previous = False
                elif i > self.front_matter_section_index and i < self.body_section_index: # Sections 1 to N (Front Matter)
                    num_style = front_format
                    run = footer_para.add_run()
                    self._add_page_number_field(run, style=num_style)
                    # Apply font style
                    num_font_style = self.guideline_mgr.get_formatting_rule('report', 'page_number')
                    if num_font_style: run.font.name = num_font_style.get('font', 'Times New Roman'); run.font.size = num_font_style.get('size', Pt(10))
                    else: run.font.name = 'Times New Roman'; run.font.size = Pt(10)
                    # Link to previous (Section 1) if i > 1, unlink Section 1 from Section 0
                    footer.is_linked_to_previous = (i > 1)
                    print(f"      Section {i} (Front Matter): Applied '{num_style}' page numbering. Link={footer.is_linked_to_previous}")
                elif i >= self.body_section_index: # Body Sections
                    num_style = body_format
                    run = footer_para.add_run()
                    self._add_page_number_field(run, style=num_style) # Arabic is default field code
                    # Apply font style
                    num_font_style = self.guideline_mgr.get_formatting_rule('report', 'page_number')
                    if num_font_style: run.font.name = num_font_style.get('font', 'Times New Roman'); run.font.size = num_font_style.get('size', Pt(10))
                    else: run.font.name = 'Times New Roman'; run.font.size = Pt(10)
                    # Unlink the *first* body section footer from front matter, link subsequent ones
                    footer.is_linked_to_previous = (i > self.body_section_index)
                    print(f"      Section {i} (Body): Applied '{num_style}' page numbering. Link={footer.is_linked_to_previous}")

            # --- Page Number Restart for Body Section ---
            if self.body_section_index > 0 and self.body_section_index < len(self.doc.sections):
                body_section = self.doc.sections[self.body_section_index]
                sectPr = body_section._sectPr
                pgNumType = sectPr.find(qn('w:pgNumType'))
                if pgNumType is None: pgNumType = OxmlElement('w:pgNumType'); sectPr.append(pgNumType)
                pgNumType.set(qn('w:start'), '1') # Restart at 1
                if qn('w:fmt') in pgNumType.attrib: del pgNumType.attrib[qn('w:fmt')] # Let field control format
                print(f"      Configured Section {self.body_section_index} to restart page numbering at 1.")

        except Exception as e: print(f"ERROR applying page numbering: {e}"); import traceback; traceback.print_exc()

    # --- Dynamic List Generation (REVISED TOC) ---

    def _find_placeholder_paragraph(self, placeholder_text):
        # ... (Find placeholder as before) ...
        if placeholder_text in self.placeholder_paragraphs: return self.placeholder_paragraphs[placeholder_text]
        for p in self.doc.paragraphs:
            if placeholder_text == p.text: self.placeholder_paragraphs[placeholder_text] = p; return p
        return None

    def _add_list_entry(self, text: str, indent_value: Inches, placeholder_para, item_style_key: str, doc_type: str):
        """Inserts list entry before placeholder with indentation and right-aligned tab for page number."""
        # Use placeholder dots for page number for now
        text_with_tab = f"{text}\t..."

        # Insert *before* the placeholder paragraph. Must iterate headings in reverse if using this.
        new_para = placeholder_para.insert_paragraph_before(text_with_tab)
        if not new_para: print(f"Warning: Failed to insert paragraph for '{text[:30]}...'"); return

        # Apply base style and specific indentation
        self._apply_paragraph_format(new_para, item_style_key, doc_type)
        new_para.paragraph_format.left_indent = indent_value

        # Define and add the right-aligned tab stop
        tab_stops = new_para.paragraph_format.tab_stops
        try:
            # Use the section where the placeholder exists to get margins
            placeholder_sect = None
            for section in self.doc.sections:
                # This check is approximate; assumes placeholder isn't split across sections
                if placeholder_para._element in section._sectPr.xpath('.//w:p'): # Crude check
                    placeholder_sect = section
                    break
            if placeholder_sect is None: placeholder_sect = self.doc.sections[-1] # Fallback

            page_width = placeholder_sect.page_width
            right_margin = placeholder_sect.right_margin
            # Calculate position slightly inside the right margin
            right_margin_pos = page_width - right_margin - Inches(0.1)

            # Ensure tab position is valid (must be > 0 and ideally > left_indent)
            if right_margin_pos > max(Inches(0), indent_value or Inches(0)):
                # Clear existing tabs before adding? May not be necessary unless styles interfere.
                # tab_stops.clear_all()
                tab_stops.add_tab_stop(right_margin_pos, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS) # Add leader dots
            else:
                print(f"      Warning: Invalid calculated tab stop position ({right_margin_pos.inches}\") <= indent ({indent_value.inches if indent_value else 0}\") for item: {text[:30]}...")
                # Fallback: Just use text without tab?
                new_para.text = text # Overwrite text_with_tab if tab fails

        except Exception as e:
            print(f"      Warning: Error adding tab stop for '{text[:30]}...': {e}")
            # Fallback: Just use text without tab?
            new_para.text = text


    def generate_toc(self, doc_type="report"):
        """Generates Table of Contents (Levels 1-3) with indentation and page placeholders."""
        placeholder_para = self._find_placeholder_paragraph(TOC_PLACEHOLDER)
        if not placeholder_para: print(f"Warning: {TOC_PLACEHOLDER} not found."); return
        print(f"      Generating Table of Contents (Levels 1-3)...")
        item_style_key = "list_entry"
        # Iterate headings in REVERSE order because we use insert_paragraph_before
        for heading_info in reversed(self.headings):
             indent_level = heading_info.get('level', 1) - 1
             # Adjust multiplier for desired visual indentation per level
             indent_value = Inches(0.4 * indent_level)
             text = heading_info.get('text', '[Missing Heading]')
             self._add_list_entry(text, indent_value, placeholder_para, item_style_key, doc_type)
        # Clear the original placeholder text AFTER adding all entries
        placeholder_para.text = ""
        print(f"      TOC generation complete.")

    def generate_lof(self, doc_type="report"):
        """Generates List of Figures with page placeholders."""
        placeholder_para = self._find_placeholder_paragraph(LOF_PLACEHOLDER)
        if not placeholder_para: print(f"Warning: {LOF_PLACEHOLDER} not found."); return
        print(f"      Generating List of Figures..."); item_style_key = "list_entry"
        for fig_info in reversed(self.figures):
             text = fig_info.get('full_caption', '[Missing Figure Caption]')
             self._add_list_entry(text, Inches(0), placeholder_para, item_style_key, doc_type) # No indent
        placeholder_para.text = ""; print(f"      LoF generation complete.")

    def generate_lot(self, doc_type="report"):
        """Generates List of Tables with page placeholders."""
        placeholder_para = self._find_placeholder_paragraph(LOT_PLACEHOLDER)
        if not placeholder_para: print(f"Warning: {LOT_PLACEHOLDER} not found."); return
        print(f"      Generating List of Tables..."); item_style_key = "list_entry"
        for table_info in reversed(self.tables):
             text = table_info.get('full_caption', '[Missing Table Caption]')
             self._add_list_entry(text, Inches(0), placeholder_para, item_style_key, doc_type) # No indent
        placeholder_para.text = ""; print(f"      LoT generation complete.")

    # --- Finalization ---
    def finalize_document(self):
        # ... (Call list generation and page numbering as before) ...
        print("    Finalizing document: Generating Lists and applying Page Numbers...")
        self.generate_toc(); self.generate_lof(); self.generate_lot()
        self.apply_page_numbering(); print("    Document finalized.")

    def save_document(self, filename: str):
        # ... (Save document as before) ...
        output_path = Path(filename); output_path.parent.mkdir(parents=True, exist_ok=True)
        try: self.doc.save(output_path); print(f"    Document successfully saved to: {output_path}")
        except PermissionError: print(f"ERROR: Permission denied saving to {output_path}. Is file open?")
        except Exception as e: print(f"ERROR: Failed to save document: {e}"); import traceback; traceback.print_exc()