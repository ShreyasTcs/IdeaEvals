"""
Innovation Idea Classifier
Classifies ideas into AI Themes, Industries, and extracts Technologies
Uses comprehensive theme definitions for accurate classification
"""

import json
from typing import Dict, List
from dataclasses import dataclass, asdict
from llm.llm_provider import LLMProvider
from core.classification.theme_definitions import THEME_DEFINITIONS


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
   
    INDUSTRIES = {
        "I1": "Banking, Financial Services & Insurance (BFSI)",
        "I2": "Communication, Media & Technology (CMT)",
        "I3": "Consumer Business (Retail & CPG)",
        "I4": "Life Sciences & Healthcare (LSH)",
        "I5": "Manufacturing (MFG)",
        "I6": "Energy, Resources & Utilities (ERU)",
        "I7": "Travel, Transportation & Hospitality (TTH)",
        "I8": "Technology, Software & Services (TechSS)"
    }
   
    def __init__(self, llm_provider: LLMProvider):
        """Initialize classifier"""
        self.llm_provider = llm_provider

    # ---------- Helper Methods ----------

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """Call LLM with system and user messages"""
        combined_prompt = f"{system_message}\n\n{user_message}\n\nIMPORTANT: Return ONLY valid JSON."
        response = self.llm_provider.generate_text(combined_prompt)
        text = response.strip()

        # Clean up markdown wrappers if LLM returns JSON inside ``` blocks
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        return text

    def _parse_json(self, response: str) -> Dict:
        """Safely parse JSON from LLM output"""
        try:
            data = json.loads(response)
            if isinstance(data, list):  # Handle list wrapping
                data = data[0]
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON structure returned by LLM.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ LLM returned invalid JSON: {e}\nResponse: {response}")

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
        
        # In tcs_classifier.py, replace your system_message with:

        SYSTEM_MESSAGE = """You are an expert at TCS specializing in AI innovation classification.
        CRITICAL RULES:
        1. Do NOT include quotes inside string values
        2. If a value contains quotes, escape them as \"
        3. Do NOT create nested objects as string values
        4. Use proper JSON syntax with double quotes only.
        5. RETURN ONLY RAW JSON - NO MARKDOWN, NO CODE BLOCKS

        Perform THREE tasks in ONE response:


        TASK 1 - THEME CLASSIFICATION:
        {theme_context}


        Classify into one of the 21 AI themes:
        - Select PRIMARY theme that best matches core purpose
        - Identify up to 3 SECONDARY themes if applicable
        - Provide confidence score (0.0 to 1.0)
        - Explain reasoning with specific references to theme definitions


        TASK 2 - INDUSTRY CLASSIFICATION:
        Map to TCS Industry:
        - Banking, Financial Services & Insurance (BFSI)
        - Communication, Media & Technology (CMT)
        - Consumer Business (Retail & CPG)
        - Life Sciences & Healthcare (LSH)
        - Manufacturing (MFG)
        - Energy, Resources & Utilities (ERU)
        - Travel, Transportation & Hospitality (TTH)
        - Technology, Software & Services (TechSS)


        TASK 3 - COMPREHENSIVE TECHNOLOGY EXTRACTION:


        Extract ALL technologies, tools, frameworks, platforms, and technical components mentioned or implied in the idea.


        TECHNOLOGY CATEGORIES TO IDENTIFY:


        1. AI/ML Technologies:
        - AI Models: GPT-4, Claude, Gemini, LLaMA, BERT, etc.
        - ML Frameworks: TensorFlow, PyTorch, Scikit-learn, Keras, JAX
        - ML Techniques: Deep Learning, NLP, Computer Vision, Reinforcement Learning
        - AI Services: OpenAI API, Azure AI, Google AI, AWS SageMaker


        2. Programming Languages & Runtimes:
        - Languages: Python, JavaScript, Java, C++, Go, Rust, TypeScript
        - Runtimes: Node.js, Deno, .NET, JVM


        3. Cloud Platforms & Infrastructure:
        - Cloud Providers: AWS, Azure, Google Cloud, IBM Cloud
        - Services: Lambda, EC2, S3, Cloud Functions, Cloud Run
        - Container Tech: Docker, Kubernetes, OpenShift


        4. Databases & Data Storage:
        - SQL: PostgreSQL, MySQL, Oracle, SQL Server
        - NoSQL: MongoDB, Cassandra, Redis, DynamoDB
        - Vector DBs: Pinecone, Weaviate, Milvus, Chroma
        - Data Warehouses: Snowflake, BigQuery, Redshift


        5. Web & Mobile Technologies:
        - Frontend: React, Angular, Vue.js, Next.js, Flutter
        - Backend: Express, FastAPI, Django, Spring Boot
        - Mobile: React Native, Swift, Kotlin, Flutter


        6. DevOps & Tools:
        - CI/CD: Jenkins, GitHub Actions, GitLab CI, CircleCI
        - Monitoring: Prometheus, Grafana, DataDog, New Relic
        - Version Control: Git, GitHub, GitLab, Bitbucket


        7. Data Processing & Analytics:
        - Big Data: Hadoop, Spark, Kafka, Flink
        - ETL: Airflow, dbt, Talend, Informatica
        - Analytics: Tableau, Power BI, Looker, Metabase


        8. Enterprise & Business Systems:
        - ERP: SAP, Oracle ERP, Microsoft Dynamics
        - CRM: Salesforce, HubSpot, Microsoft Dynamics CRM
        - Collaboration: Microsoft Teams, Slack, Zoom


        9. IoT & Edge Computing:
        - IoT Platforms: AWS IoT, Azure IoT, Google IoT Core
        - Edge: Edge TPU, NVIDIA Jetson, Raspberry Pi
        - Protocols: MQTT, CoAP, LoRaWAN


        10. Security & Authentication:
            - Auth: OAuth, JWT, SAML, Active Directory
            - Security: SSL/TLS, VPN, Firewall, WAF
            - Tools: Vault, KeyCloak, Auth0


        11. APIs & Integration:
            - API Types: REST, GraphQL, gRPC, WebSocket
            - API Management: Apigee, Kong, AWS API Gateway
            - Integration: MuleSoft, Dell Boomi, Apache Camel


        12. Specialized Technologies:
            - Blockchain: Ethereum, Hyperledger, Solidity
            - AR/VR: Unity, Unreal Engine, ARKit, ARCore
            - Quantum: Qiskit, Cirq, Q#


        EXTRACTION RULES:
        1. Extract EXPLICIT mentions (directly stated technologies)
        2. Extract IMPLICIT technologies (inferred from context)
        3. Include version numbers if mentioned (e.g., "Python 3.11")
        4. Normalize names (e.g., "k8s" → "Kubernetes")
        5. Group related technologies logically
        6. Prioritize specific over generic (e.g., "GPT-4" over "AI")
        7. Include both commercial and open-source technologies
        8. Extract technical methodologies (e.g., "microservices", "serverless")
        9. Include hardware if mentioned (e.g., "GPU", "TPU", "NVIDIA A100")
        10. Extract data formats and protocols (e.g., "JSON", "REST API", "MQTT")


        QUALITY CRITERIA:
        - Minimum 5 technologies (unless idea is very simple)
        - Maximum 20 technologies (focus on most relevant)
        - Order by relevance and specificity
        - Avoid duplicates and redundancy
        - Include both core and supporting technologies


        Return this exact structure:
        {{
        "theme": {{
            "primary_theme": "Theme name here",
            "secondary_themes": ["Theme1", "Theme2"],
            "confidence": 0.95,
            "rationale": "Explanation here"
        }},
        "industry": {{
            "industry_name": "Industry name",
            "confidence": 0.95,
            "rationale": "Explanation here"
        }},
        "technologies": {{
            "technologies_extracted": ["Tech1", "Tech2"],
            "rationale": "Explanation here"
        }}
        }}
        """

        # Then use it like this:
        system_message = SYSTEM_MESSAGE.format(
                theme_context=theme_context,
                submission_text=idea_text
            )        
        user_message = f"Classify this AI innovation idea:\n\n{idea_text}"
        response = self._call_llm(system_message, user_message)
        data = self._parse_json(response)
        
        return data
