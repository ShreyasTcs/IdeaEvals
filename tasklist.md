# Backend Refactoring Task List

This file tracks the progress of refactoring the backend to be modular and independent of specific data sources or LLM providers.

- [ ] **Task 1: Changes to be made**
  - [ ] The output json has to be continually updated so that new output can be stored continually so that in case the system stops , the results will be still be stored and the output json can be processed continually to do additional things.
  - [ ] The additional file types for that idea has to be also stored in the output schema in the form of list with all types of the additional type associated with the idea present in the additional folder.
  - [ ] Develop a frontend application for the hackathon evaluation application where the organizer will be able to configure and upload files to be able to evaluate the hackathon ideas. It must allow the organizer to create a new evaluation task where it will ask him for the hackathon details like hackathon name, description then it will ask for hackathon related details like the rubrics where default rubrics are pre-populated and displayed to users. The system must allow users to add, edit, delete, and reorder rubric items. The added rubrics must ask the rubrics name, description(must give an option to allow users to AI generate the description using azure openai), weights and scoring scale anchor. These must have a default value that can be changed by the user. For default value use the data in schema.json(change this to fit the data needed as given above). The selected/edited rubrics should be submitted to the backend and passed into the pipeline through input_helper.py, and the selected rubrics must be applied throughout the entire processing pipeline. The frontend should allow users to upload the same CSV file that already exists in the backend data folder (for demo purposes), and also specify additional file URLs that correspond to the additional files already present in the backend data folder. While processing, the frontend must display progress indicators (live updates from the backend), and once the pipeline finishes, the frontend must show the results both statistically and visually, including information like top 10 highest-scoring ideas, overall statistics across all ideas, and other interpretive visualizations.
  - [ ] The evaluation_user_prompt must use the rubircs (that is given through the input_helper from the frontend) to evaluate the ideas. The rubrics format must be in such a way that it will provide these info:EXPERT EVALUATION CRITERIA & QUESTIONS (weights in parentheses):
1) NOVELTY (15%)
  - Problem significance; differentiation vs alternatives; market gap; category creation/disruption.
2) CLARITY (20%)
  - What/how/for whom; personas & buyers; value prop; differentiators; domain understanding.
3) FEASIBILITY (20%)
  - Technical approach credibility; integration complexity; resources & timeline; risks & mitigations; regulatory constraints.
4) LONG_TERM_VALUE (20%)
  - Business model; GTM; scalability; defensibility/switching costs; TAM expansion; enterprise trend alignment.
5) SECURITY_COMPLIANCE (15%)
  - Data handling (PII/PHI); authN/authZ; encryption (in transit/at rest); key mgmt; audit logging; AI misuse safeguards; regulatory mapping (GDPR, HIPAA, PCI DSS, ISO 27001, SOC 2).
6) EVIDENCE (10%)
  - PoC/demo; benchmarks/metrics; user feedback; references; professional completeness.

SCORING SCALE ANCHORS (1–10): 9–10 Outstanding | 7–8 Strong | 5–6 Fair | 3–4 Weak | 1–2 Poor. that is the rubrics will provide info about the rubrics name, description, weight and scoring scale anchor(for evaluation). It must also give in the prompt to increase the total score by 2 incase the content_type(given from the extraction) in the prompt is "prototype".