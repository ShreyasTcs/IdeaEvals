"""
Comprehensive Theme Definitions for TCS Ideathon Classification System

This module provides detailed, researched definitions for all 21 AI themes used in the classification system. Each theme includes:
- Technical definition
- TCS business context  
- Concrete examples
- Valid domain classifications
- Keywords for identification

Author: Enhanced Classification System
"""

THEME_DEFINITIONS = {
    # Functional themes
    "AI for Industry": {
        "definition": "AI solutions designed for specific industry verticals, addressing industry-unique challenges and leveraging domain expertise",
        "tcs_context": "Aligns with TCS industry-specific solutions across Financial Services, Manufacturing, Healthcare, Retail, Energy, Public Services",
        "examples": ["Banking fraud detection", "Manufacturing predictive maintenance", "Healthcare diagnostics", "Retail personalization"],
        "domains": ["Banking", "Manufacturing", "Healthcare", "Retail", "Energy", "Utilities", "Government", "Insurance", "Telecommunications"],
        "keywords": ["industry", "vertical", "sector-specific", "domain expertise"]
    },
    "AI in Service lines": {
        "definition": "AI applications within specific business service areas or functional domains within enterprises",
        "tcs_context": "Maps to TCS service offerings like Consulting, Cognitive Business Operations, Digital Transformation, Infrastructure Services",
        "examples": ["HR talent analytics", "Finance automation", "Supply chain optimization", "Customer service enhancement"],
        "domains": ["HR", "Finance", "Operations", "Marketing", "Sales", "Procurement", "Legal", "Customer Service"],
        "keywords": ["service lines", "business functions", "enterprise services"]
    },
    "AI for TCS": {
        "definition": "AI initiatives specifically designed to enhance TCS internal operations, employee experience, or service delivery capabilities",
        "tcs_context": "Internal TCS applications improving consultant productivity, project delivery, knowledge management, organizational efficiency",
        "examples": ["Employee engagement platforms", "Project management assistants", "Knowledge sharing systems", "Consultant productivity tools"],
        "domains": ["Employee Experience", "Project Delivery", "Knowledge Management", "Talent Development", "Operations", "Learning"],
        "keywords": ["TCS internal", "consultant productivity", "organizational efficiency"]
    },
    
    # Deployment
    "Virtual workers / Copilots": {
        "definition": "AI-powered assistants that work alongside humans as intelligent partners, providing context-aware guidance and task automation",
        "tcs_context": "Digital workforce solutions that augment human capabilities in client engagements and internal operations",
        "examples": ["Code copilots", "Document assistants", "Meeting coordinators", "Research assistants"],
        "domains": ["Software Development", "Documentation", "Research", "Customer Support", "Content Creation"],
        "keywords": ["copilot", "virtual worker", "assistant", "augmentation"]
    },
    "Edge AI": {
        "definition": "AI algorithms deployed directly on local edge devices enabling real-time data processing without cloud dependency",
        "tcs_context": "IoT and edge computing solutions for manufacturing, smart cities, and real-time decision making",
        "examples": ["IoT sensor analytics", "Real-time video processing", "Autonomous vehicle systems", "Smart device intelligence"],
        "domains": ["IoT", "Manufacturing", "Automotive", "Smart Cities", "Real-time Processing"],
        "keywords": ["edge computing", "local processing", "real-time", "IoT"]
    },
    "Agents & APIs": {
        "definition": "Autonomous AI agents that can interact with external systems and APIs to accomplish complex tasks independently",
        "tcs_context": "Integration solutions that connect AI capabilities with enterprise systems and third-party services",
        "examples": ["API orchestration agents", "System integration bots", "Workflow automation agents", "Service mesh coordinators"],
        "domains": ["System Integration", "API Management", "Workflow Automation", "Enterprise Architecture"],
        "keywords": ["agents", "APIs", "integration", "automation"]
    },
    "Multi-modal UX": {
        "definition": "User experiences that support multiple input/output modes including visual, auditory, touch, and gesture interactions",
        "tcs_context": "Advanced user interface solutions for accessibility, immersive experiences, and natural human-computer interaction",
        "examples": ["Voice-enabled interfaces", "Gesture recognition systems", "Mixed reality experiences", "Accessibility solutions"],
        "domains": ["User Experience", "Accessibility", "Voice Interfaces", "Gesture Recognition", "AR/VR"],
        "keywords": ["multimodal", "voice", "gesture", "accessibility", "natural interaction"]
    },
    
    # AI techniques
    "Classical AI/ML/DL for prediction / recommendations": {
        "definition": "Traditional machine learning and deep learning approaches focused on prediction, classification, and recommendation systems",
        "tcs_context": "Foundation AI/ML capabilities used across TCS solutions for predictive analytics and recommendation engines",
        "examples": ["Predictive maintenance models", "Recommendation engines", "Classification systems", "Time series forecasting"],
        "domains": ["Predictive Analytics", "Recommendation Systems", "Classification", "Forecasting", "Pattern Recognition"],
        "keywords": ["machine learning", "deep learning", "prediction", "classification", "recommendation"]
    },
    "GenAI & its techniques": {
        "definition": "Generative AI systems that create original content including text, images, code, and other media based on prompts and training",
        "tcs_context": "TCS AI WisdomNext and generative AI solutions for content creation, code generation, and creative applications",
        "examples": ["Text generation", "Code synthesis", "Image creation", "Document automation", "Creative content"],
        "domains": ["Content Creation", "Code Generation", "Document Automation", "Creative AI", "Text Processing"],
        "keywords": ["generative AI", "content creation", "text generation", "code synthesis"]
    },
    "Agentic AI": {
        "definition": "Autonomous AI systems that proactively set and pursue complex goals with minimal human intervention, using reasoning and planning",
        "tcs_context": "Advanced AI solutions that can independently manage complex workflows and make strategic decisions",
        "examples": ["Strategic planning agents", "Autonomous project managers", "Independent research systems", "Self-managing workflows"],
        "domains": ["Strategic Planning", "Project Management", "Research", "Workflow Management", "Decision Making"],
        "keywords": ["autonomous", "proactive", "reasoning", "planning", "independent"]
    },
    "Orchestration & MCP": {
        "definition": "AI orchestration systems and Model Context Protocol implementations for coordinating multiple AI services and data sources",
        "tcs_context": "Enterprise AI infrastructure for managing complex AI workflows and integrating multiple AI capabilities",
        "examples": ["AI workflow orchestration", "Multi-model coordination", "Context sharing systems", "AI service mesh"],
        "domains": ["AI Infrastructure", "Workflow Orchestration", "System Integration", "Multi-model Systems"],
        "keywords": ["orchestration", "MCP", "workflow", "coordination", "integration"]
    },
    "Deep-tech research": {
        "definition": "Advanced research in cutting-edge AI technologies, algorithms, and theoretical foundations with long-term innovation focus",
        "tcs_context": "TCS research initiatives in advanced AI, quantum computing, and next-generation computational methods",
        "examples": ["Novel AI algorithms", "Quantum-AI hybrid systems", "Advanced neural architectures", "Theoretical AI research"],
        "domains": ["Research", "Algorithm Development", "Quantum Computing", "Neural Architecture", "Theoretical AI"],
        "keywords": ["research", "deep tech", "advanced algorithms", "innovation", "theoretical"]
    },
    "AI for creative": {
        "definition": "AI systems focused on creative applications including art, music, design, storytelling, and other creative domains",
        "tcs_context": "Creative AI solutions for marketing, media, and entertainment industries served by TCS",
        "examples": ["AI art generation", "Music composition", "Creative writing", "Design automation", "Brand creation"],
        "domains": ["Art Generation", "Music", "Creative Writing", "Design", "Media", "Entertainment"],
        "keywords": ["creative", "art", "music", "design", "storytelling"]
    },
    
    # Models
    "Open source / Open weight models": {
        "definition": "AI models with publicly available source code, weights, or architectures that can be freely used and modified",
        "tcs_context": "Cost-effective AI solutions leveraging open source models for client implementations and internal tools",
        "examples": ["Open source LLMs", "Community models", "Apache/MIT licensed models", "Hugging Face models"],
        "domains": ["Open Source", "Community Models", "Cost Optimization", "Model Customization"],
        "keywords": ["open source", "open weights", "community", "free", "customizable"]
    },
    "Proprietary models": {
        "definition": "Commercial AI models developed by companies like OpenAI, Anthropic, Google with licensed access and usage restrictions",
        "tcs_context": "Premium AI capabilities using commercial models for high-performance client solutions",
        "examples": ["GPT models", "Claude", "Gemini", "Commercial vision models", "Enterprise AI APIs"],
        "domains": ["Commercial AI", "Premium Services", "Enterprise APIs", "Licensed Models"],
        "keywords": ["proprietary", "commercial", "licensed", "premium", "enterprise"]
    },
    "Pre-built partner solutions": {
        "definition": "Ready-to-use AI solutions developed by technology partners and vendors for specific use cases and industries",
        "tcs_context": "TCS partnerships with AI vendors to deliver proven solutions quickly to clients",
        "examples": ["Partner AI platforms", "Industry-specific AI tools", "Vendor solutions", "Third-party AI services"],
        "domains": ["Partner Solutions", "Vendor Platforms", "Industry Tools", "Third-party Services"],
        "keywords": ["partner", "pre-built", "vendor", "ready-to-use", "third-party"]
    },
    
    # Common minimum foundations
    "Responsible AI": {
        "definition": "AI development practices ensuring fairness, transparency, accountability, privacy, and ethical use of AI systems",
        "tcs_context": "TCS commitment to ethical AI development and deployment across all client solutions and internal systems",
        "examples": ["Bias detection systems", "AI explainability tools", "Privacy-preserving AI", "Ethical guidelines"],
        "domains": ["Ethics", "Fairness", "Transparency", "Privacy", "Governance", "Compliance"],
        "keywords": ["responsible", "ethical", "fairness", "transparency", "governance"]
    },
    "AI for Data & Data for AI": {
        "definition": "AI systems for data management, quality, and preparation, plus data strategies that enable effective AI implementation",
        "tcs_context": "Data foundation services and AI-powered data solutions across TCS data analytics offerings",
        "examples": ["Data quality AI", "Automated data prep", "Data discovery", "AI training data curation"],
        "domains": ["Data Quality", "Data Preparation", "Data Discovery", "Training Data", "Data Engineering"],
        "keywords": ["data quality", "data preparation", "training data", "data engineering"]
    },
    "AI for CyberSecurity & CyberSecurity for AI": {
        "definition": "AI applications in cybersecurity defense and security measures to protect AI systems from attacks and vulnerabilities",
        "tcs_context": "TCS cybersecurity services enhanced with AI and security frameworks for protecting AI implementations",
        "examples": ["AI threat detection", "Automated incident response", "AI model security", "Adversarial attack defense"],
        "domains": ["Cybersecurity", "Threat Detection", "Incident Response", "Model Security", "AI Safety"],
        "keywords": ["cybersecurity", "threat detection", "security", "protection", "defense"]
    },
    "AI Observability & FinOps for AI": {
        "definition": "Monitoring, observability, and financial operations for AI systems including cost management and performance optimization",
        "tcs_context": "AI operations and cost optimization services for enterprise AI deployments and cloud AI spending",
        "examples": ["AI performance monitoring", "Cost optimization", "Resource management", "AI ops dashboards"],
        "domains": ["Monitoring", "Cost Management", "Performance", "Operations", "Resource Optimization"],
        "keywords": ["observability", "FinOps", "monitoring", "cost management", "performance"]
    },
    "AI in software engineering lifecycle": {
        "definition": "AI applications throughout software development including coding, testing, deployment, and maintenance phases",
        "tcs_context": "TCS software engineering services enhanced with AI for improved development productivity and quality",
        "examples": ["AI code generation", "Automated testing", "Bug detection", "Code review automation"],
        "domains": ["Software Development", "Testing", "Code Review", "DevOps", "Quality Assurance"],
        "keywords": ["software engineering", "development lifecycle", "coding", "testing", "DevOps"]
    },
    "AI for accessibility": {
        "definition": "AI solutions designed to improve accessibility and inclusion for people with disabilities and diverse needs",
        "tcs_context": "Inclusive design and accessibility solutions across TCS applications and client systems",
        "examples": ["Voice recognition for disabilities", "Visual assistance tools", "Text-to-speech", "Cognitive accessibility"],
        "domains": ["Accessibility", "Inclusion", "Assistive Technology", "Universal Design"],
        "keywords": ["accessibility", "inclusion", "assistive", "disability support", "universal design"]
    }
}
