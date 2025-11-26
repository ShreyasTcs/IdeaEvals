# Backend Refactoring Task List

This file tracks the progress of refactoring the backend to be modular and independent of specific data sources or LLM providers.

- [x] **Task 1: Changes to be made**
  - [x] Create a Python helper script that generates a JSON output and stores the results in a PostgreSQL database. Design a comprehensive schema consisting of multiple interconnected tables, ensuring that each table is responsible for a specific aspect of the data. This approach minimizes redundancy and maintains security, structure, and clarity. Separate components, such as hackathon details, user information, rubric configurations, submissions, judging results, and comments, should each be stored in distinct tables. Ensure that relationships between these tables are well-defined using foreign keys. Additionally, include code to create the necessary tables when the script runs, specifically after the user sets up the hackathon and configures the rubrics. This initialization should happen at the start of the process to ensure the database structure is ready for storing data. 
