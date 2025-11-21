"""
Innovation Idea Classifier
Classifies ideas into AI Themes, Industries, and extracts Technologies
Uses comprehensive theme definitions for accurate classification
"""

from typing import Dict, List
from dataclasses import dataclass, asdict
from pathlib import Path
from llm.llm_provider import LLMProvider
from core.classification.theme_definitions import THEME_DEFINITIONS
from utils.industries import INDUSTRIES
from utils.llm_utils import call_llm, parse_json


# ---------- Data Models ----------

@dataclass
class ThemeClassification:
    primary_theme: str
    secondary_themes: List[str]
    confidence: float
    rationale: str


@dataclass
class IndustryClassification:
    industry_name: str
    confidence: float
    rationale: str


@dataclass
class TechnologyExtraction:
    technologies_extracted: List[str]
    rationale: str


# ---------- Main Class ----------

class TCSClassifier:
    """Main classifier for innovation ideas using comprehensive AI theme definitions"""
   
    # AI Themes from comprehensive definitions
    AI_THEMES = list(THEME_DEFINITIONS.keys())
   
    def __init__(self, llm_provider: LLMProvider):
        """Initialize classifier"""
        self.llm_provider = llm_provider

    # ---------- Classification Method (Single API Call) ----------

    def classify_all(self, idea_text: str) -> Dict:
        """Run all classifications in a single API call"""
        
        # Build detailed theme context from definitions
        theme_context = "AI THEME DEFINITIONS:\n\n"
        for idx, (theme_name, theme_info) in enumerate(THEME_DEFINITIONS.items(), 1):
            theme_context += f"{idx}. {theme_name}\n"
            theme_context += f"   Definition: {theme_info['definition']}\n"
            theme_context += f"   TCS Context: {theme_info['tcs_context']}\n"
            theme_context += f"   Examples: {', '.join(theme_info['examples'])}\n"
            theme_context += f"   Keywords: {', '.join(theme_info['keywords'])}\n\n"
        
        # Load the system prompt from a file
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        with open(prompts_dir / "classification_system_prompt.txt", "r") as f:
            system_message_template = f.read()

        # Then use it like this:
        system_message = system_message_template.format(
                theme_context=theme_context,
                submission_text=idea_text
            )        
        user_message = f"Classify this AI innovation idea:\n\n{idea_text}"
        response = call_llm(self.llm_provider, system_message, user_message)
        data = parse_json(response)
        
        return data
