from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

from llm.llm_provider import LLMProvider
from core.classification.tcs_classifier import TCSClassifier
from core.evaluation.idea_evaluator import IdeaEvaluator
from core.extraction.file_extractor import FileExtractor
from core.verification.verification_processor import VerificationProcessor

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
        self.verifier = VerificationProcessor(rubrics)

    def process_idea(self, idea_data: Dict[str, Any], additional_files_dir: Path) -> Dict[str, Any]:
        """
        Processes a single idea through the entire pipeline.
        """
        # 1. Extract content from associated files
        idea_id = idea_data.get("idea_id")
        all_files_content = []
        content_types = []
        if idea_id:
            idea_dir = additional_files_dir / str(idea_id)
            if idea_dir.is_dir():
                for file_path in idea_dir.iterdir():
                    if file_path.is_file():
                        extraction_result = self.extractor.extract_content(file_path)
                        all_files_content.append(f"--- START OF FILE: {file_path.name} ---\n{extraction_result['text']}\n--- END OF FILE: {file_path.name} ---\n")
                        if 'content_type' in extraction_result:
                            content_types.append(extraction_result['content_type'])

        idea_data['extracted_files_content'] = "\n".join(all_files_content)
        
        # Determine overall content type
        overall_content_type = "Text"
        if "Prototype" in content_types:
            overall_content_type = "Prototype"
        idea_data['content_type'] = overall_content_type
        
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
        # Load prompts from files
        prompts_dir = Path(__file__).parent.parent / "prompts"
        with open(prompts_dir / "evaluation_system_prompt.txt", "r") as f:
            system_prompt = f.read()
        with open(prompts_dir / "evaluation_user_prompt.txt", "r") as f:
            user_prompt_template = f.read()
        
        evaluation_result = self.evaluator.evaluate_idea(
            idea_data=idea_data,
            base_system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            rubrics=self.rubrics
        )
        idea_data['evaluation'] = evaluation_result

        # 4. Verify the evaluation
        verification_result = self.verifier.verify_evaluation(evaluation_result)
        idea_data['verification'] = verification_result

        return idea_data
