from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

from llm.llm_provider import LLMProvider
from core.classification.tcs_classifier import TCSClassifier
from core.evaluation.idea_evaluator import IdeaEvaluator
from core.extraction.file_extractor import FileExtractor

class IdeaProcessor:
    """
    Orchestrates the processing of a single idea, including file extraction,
    classification, and evaluation.
    """

    def __init__(self, llm_provider: LLMProvider, rubrics: Dict[str, float]):
        self.llm_provider = llm_provider
        self.rubrics = rubrics
        self.classifier = TCSClassifier(llm_provider)
        self.evaluator = IdeaEvaluator(llm_provider)
        self.extractor = FileExtractor()

    def process_idea(self, idea_data: Dict[str, Any], additional_files_dir: Path) -> Dict[str, Any]:
        """
        Processes a single idea through the entire pipeline.
        """
        # 1. Extract content from associated files
        idea_id = idea_data.get("idea_id")
        all_files_content = []
        if idea_id:
            idea_dir = additional_files_dir / str(idea_id)
            if idea_dir.is_dir():
                for file_path in idea_dir.iterdir():
                    if file_path.is_file():
                        extraction_result = self.extractor.extract_content(file_path)
                        all_files_content.append(f"--- START OF FILE: {file_path.name} ---\n{extraction_result['text']}\n--- END OF FILE: {file_path.name} ---\n")

        idea_data['extracted_files_content'] = "\n".join(all_files_content)
        logger.debug(f"Extracted content for idea {idea_id}: {idea_data['extracted_files_content'][:1000]}...")

        # 2. Classify the idea
        # Create a combined text for classification
        text_for_classification = f"""
        Title: {idea_data.get('idea_title', '')}
        Summary: {idea_data.get('brief_summary', '')}
        Challenge: {idea_data.get('challenge_opportunity', '')}
        Novelty: {idea_data.get('novelty_benefits_risks', '')}
        Responsible AI: {idea_data.get('responsible_ai', '')}
        File Content: {idea_data['extracted_files_content']}
        """
        
        classification_result = self.classifier.classify_all(text_for_classification)
        idea_data.update(classification_result)

        # 3. Evaluate the idea
        # These prompts would typically be loaded from a config or template file
        system_prompt = "You are an expert evaluator for a hackathon."
        user_prompt_template = """
        Please evaluate the following idea based on the provided rubrics.
        
        {rubric_criteria}
        
        Idea Details:
        Title: {idea_title}
        Summary: {brief_summary}
        Challenge/Opportunity: {challenge_opportunity}
        Novelty/Benefits/Risks: {novelty_benefits_risks}
        Primary Theme: {primary_theme}
        Industry: {industry_name}
        Technologies: {technologies_extracted}
        
        Extracted Content from Files:
        {extracted_files_content}
        """
        
        evaluation_result = self.evaluator.evaluate_idea(
            idea_data=idea_data,
            base_system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            rubrics=self.rubrics
        )
        idea_data['evaluation'] = evaluation_result

        return idea_data
