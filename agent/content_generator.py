# agent/content_generator.py
from .ollama_client import OllamaClient
from .guideline_manager import GuidelineManager
import config

class ContentGenerator:
    """
    Uses an OllamaClient to generate text content for different sections
    of a project report or synopsis based on project data.
    """
    DEFAULT_SYSTEM_MESSAGE = "You are a helpful academic assistant drafting sections for a student project report. Write clearly, concisely, and professionally in the third person, focusing on the provided details. Avoid making up results or specific technical details not provided, but elaborate reasonably on the given concepts. IMPORTANT: Generate ONLY the body text for the requested section. Do NOT include the section title itself or any markdown formatting (like ## or **)."

    def __init__(self, ollama_client: OllamaClient, guideline_manager: GuidelineManager):
        self.ollama_client = ollama_client
        self.guideline_mgr = guideline_manager
        print("    ContentGenerator initialized.")

    def _build_prompt(self, section_name: str, doc_type: str, project_data: dict) -> str:
        title = project_data.get('project_title', '[Project Title]')
        summary = project_data.get('project_summary', 'No summary provided.')
        objectives = project_data.get('objectives', [])
        methodology = project_data.get('methodology_tools', 'No methodology specified.')
        results = project_data.get('results_summary', 'No results summary provided.')
        conclusions = project_data.get('conclusions_future_scope', [])
        intro_hints = project_data.get('introduction_points', [])
        lit_review_hints = project_data.get('literature_review_ideas', [])

        base_context = (f"Project Title: {title}\nProject Summary: {summary}\nDocument Type: {doc_type.capitalize()}\n")
        prompt = f"{base_context}\n"
        # Reiterate core instruction
        prompt += f"Instructions: Write ONLY the body content for the '{section_name}' section. Do NOT include the section title itself or any markdown/formatting. Focus on the details below.\n\n"

        # Section-specific guidance
        if section_name == "Introduction":
            prompt += "Content Focus:\n- Briefly introduce domain/relevance.\n- State core problem/motivation.\n- Mention main objectives (use list below).\n- Outline report/synopsis structure.\n"
            if intro_hints: prompt += "Specific points to consider:\n" + "\n".join([f"- {p}" for p in intro_hints]) + "\n"
            if objectives: prompt += "Project Objectives reference:\n" + "\n".join([f"- {o}" for o in objectives]) + "\n"
            prompt += "Length: 2-4 paragraphs (Report), 1-2 paragraphs (Synopsis)."
        elif section_name == "Abstract":
            prompt += "Content Focus (under 250 words, single paragraph):\n- Purpose and scope.\n- Key methodology.\n- Main results/outcomes.\n- Primary conclusions.\n(Do NOT include references).\n"
            prompt += f"Base on: Objectives: {objectives}\nMethodology: {methodology}\nResults: {results}\nConclusions: {conclusions}"
        elif section_name == "Acknowledgement":
            supervisor = project_data.get('supervisor_name', '[Supervisor Name]'); college = project_data.get('college', '[College Name]'); dept = project_data.get('department', '[Department Name]')
            prompt += f"Content Focus:\n- Thank supervisor: {supervisor}.\n- Mention {dept} and {college}.\n- Optional general thanks (faculty, friends etc.).\nLength: 1-2 paragraphs."
        elif section_name == "Background and Literature Review":
            prompt += "Content Focus:\n- Background concepts.\n- Related work (techniques, tools, studies).\n- Gaps/limitations addressed by this project.\n"
            if lit_review_hints: prompt += "Incorporate topics/keywords:\n" + "\n".join([f"- {h}" for h in lit_review_hints]) + "\n"
            prompt += "Length: Several paragraphs (Report), 2-3 paragraphs (Synopsis).\nIMPORTANT: Describe concepts generally, do NOT invent specific citations like '[1]'."
        elif section_name == "Problem Statement and Objectives": # Synopsis focus
             prompt += "Content Focus:\n- Define the problem addressed.\n- List specific objectives (use list below or formulate plausible ones).\n"
             if objectives: prompt += "Objectives:\n" + "\n".join([f"- {o}" for o in objectives]) + "\n"
             else: prompt += "(No objectives provided; formulate based on title/summary).\n"
             prompt += "Length: 1 paragraph problem statement, bulleted objectives."
        elif section_name == "Methodology and Tools Used" or section_name == "System Design and Methodology":
             prompt += f"Content Focus:\n- Describe methodology, design, algorithms, frameworks, tools used/proposed based on: '{methodology}'.\n- Explain relevance to objectives.\n- Detail design/architecture/workflow (Report) or provide high-level overview (Synopsis)."
        elif section_name == "Implementation and Results" or section_name == "Expected Results and Contribution":
             is_report = doc_type == config.DOC_REPORT; section_title = "Implementation and Results" if is_report else "Expected Results and Contribution"
             prompt = prompt.replace(f"'{section_name}'", f"'{section_title}'") # Adjust title in intro line if needed
             if is_report:
                 prompt += f"Content Focus:\n- Implementation details.\n- Key results/findings/metrics based on: '{results}'.\n- Analysis/interpretation of results.\n- Mention figures/tables if relevant (e.g., 'Table X.Y summarizes...')."
             else: # Synopsis
                 prompt += f"Content Focus:\n- Expected outcomes.\n- How outcomes address the problem.\n- Potential significance/contribution.\nBase on expected results: '{results}'.\nLength: 1-2 paragraphs."
        elif section_name == "Conclusion and Future Scope":
             prompt += f"Content Focus:\n- Summarize project achievements vs objectives.\n- Discuss limitations.\n- Suggest future research/enhancements.\n"
             if conclusions: prompt += "Use provided points:\n" + "\n".join([f"- {c}" for c in conclusions]) + "\n"
             prompt += "Length: 1-2 paragraphs conclusion, 1 paragraph future scope."
        else: prompt += f"Write a general section about '{section_name}' based on project title/summary. Keep concise."
        prompt += f"\nEnsure output is suitable body text for a '{doc_type.capitalize()}'."
        return prompt

    def generate_section(self, section_name: str, doc_type: str, project_data: dict) -> str:
        print(f"    Generating content for section: '{section_name}' ({doc_type})...")
        prompt = self._build_prompt(section_name, doc_type, project_data)
        system_msg = self.DEFAULT_SYSTEM_MESSAGE
        generated_text = self.ollama_client.generate(prompt, system_message=system_msg)
        if not generated_text:
            print(f"      WARNING: Ollama returned empty content for '{section_name}'. Returning placeholder.")
            # Return specific placeholder to match observed output
            return f"[Content for '{section_name}' could not be generated.]"
        print(f"      Content generation successful for '{section_name}'.")
        return generated_text

    # --- Convenience methods ---
    def generate_introduction(self, doc_type: str, project_data: dict) -> str: return self.generate_section("Introduction", doc_type, project_data)
    def generate_abstract(self, project_data: dict) -> str: return self.generate_section("Abstract", config.DOC_REPORT, project_data)
    def generate_acknowledgement(self, project_data: dict) -> str: return self.generate_section("Acknowledgement", config.DOC_REPORT, project_data)
    def generate_literature_review(self, doc_type: str, project_data: dict) -> str: return self.generate_section("Background and Literature Review", doc_type, project_data)
    def generate_problem_and_objectives(self, doc_type: str, project_data: dict) -> str: return self.generate_section("Problem Statement and Objectives", doc_type, project_data)
    def generate_methodology(self, doc_type: str, project_data: dict) -> str: section_key = "System Design and Methodology" if doc_type == config.DOC_REPORT else "Methodology and Tools Used"; return self.generate_section(section_key, doc_type, project_data)
    def generate_results(self, doc_type: str, project_data: dict) -> str: section_key = "Implementation and Results" if doc_type == config.DOC_REPORT else "Expected Results and Contribution"; return self.generate_section(section_key, doc_type, project_data)
    def generate_conclusion_future_scope(self, doc_type: str, project_data: dict) -> str: return self.generate_section("Conclusion and Future Scope", doc_type, project_data)

# Example Usage (remains the same for testing structure)
if __name__ == '__main__':
    # ... (Mock classes and test execution code as before) ...
    print("--- Testing ContentGenerator ---")
    # ... (Include mock classes and test calls as in previous version) ...