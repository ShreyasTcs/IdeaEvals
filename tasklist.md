# Backend Refactoring Task List

This file tracks the progress of refactoring the backend to be modular and independent of specific data sources or LLM providers.

- [x] **Task 1: Changes to be made**
  - [x] Create a Python helper script that generates a JSON output and stores the results in a PostgreSQL database. Design a comprehensive schema consisting of multiple interconnected tables, ensuring that each table is responsible for a specific aspect of the data. This approach minimizes redundancy and maintains security, structure, and clarity. Separate components, such as hackathon details, user information, rubric configurations, submissions, judging results, and comments, should each be stored in distinct tables. Ensure that relationships between these tables are well-defined using foreign keys. Additionally, include code to create the necessary tables when the script runs, specifically after the user sets up the hackathon and configures the rubrics. This initialization should happen at the start of the process to ensure the database structure is ready for storing data.

- [x] **Task 2: Frontend-Backend Integration & Advanced Dashboard**
  - [x] **Database & Security Updates:**
    - [x] Update the `hackathons` table to include authentication fields: `passkey_hash` (for security) and a unique `access_code` (e.g., UUID or 8-char string) to uniquely identify the hackathon event.
    - [x] Create an API endpoint `POST /api/hackathon/init` that accepts the hackathon name, description, and user-provided passkey. It should generate a unique `access_code`, create the DB entry, and return the code to the user.
    - [x] Create an API endpoint `POST /api/hackathon/login` that validates the `access_code` and `passkey`, returning a session token or success status to allow access to results.

  - [x] **API Development for Data Retrieval:**
    - [x] `GET /api/hackathon/{access_code}/dashboard`: A high-performance endpoint that fetches aggregated data for the main dashboard. It should join `ideas`, `evaluations`, `classifications`, and `verifications` tables.
      - Returns: Idea ID, Title, Total Score, Primary Theme, Status (Completed/Flagged), and key rubric scores.
    - [x] `GET /api/idea/{external_idea_id}/details`: Fetches the complete deep-dive data for a single idea.
      - Returns: Full summary, extracted text, all classification rationales, specific rubric breakdowns (score + reasoning), verification warnings, and file paths.

  - [x] **Frontend: Landing & Authentication:**
    - [x] **Landing Page:** A split-screen or card-based layout offering two clear paths: "Start New Evaluation" and "View Results".
    - [x] **Creation Flow:** A wizard-style form to input Hackathon Details -> Set Passkey -> Upload Rubrics -> Upload Ideas. Displays the unique **Access Code** prominently upon completion.
    - [x] **Login Flow:** A secure entry page asking for **Access Code** and **Passkey** to unlock the dashboard.

  - [x] **Frontend: Advanced Results Dashboard:**
    - [x] **Stats Overview:** Top cards showing "Total Ideas", "Average Score", "Top Performing Theme", and "Compliance Flags".
    - [x] **Smart Data Table:**
      - **Sorting:** Clickable headers to sort by Overall Score, Novelty, Feasibility, or specific Rubric Scores.
      - **Filtering:** Dropdown filters for "Theme", "Industry", "Tech Stack", and "Verification Status" (e.g., Show only 'Flagged' ideas).
      - **Search:** A global search bar to instantly find ideas by Employee ID (Idea ID), Title, or Keywords.
    - [x] **Visualizations (Optional):** Simple bar/pie charts showing the distribution of scores and themes.

  - [x] **Frontend: Detailed Idea View:**
    - [x] A modal or dedicated page when an idea is clicked.
    - [x] **Scorecard:** A visual breakdown of rubric scores (e.g., radar chart or progress bars) with the LLM's reasoning for each.
    - [x] **Verification Badge:** Clear indicators if the idea passed verification or has warnings (hallucinations/missing info).
    - [x] **Source Data:** Accordion views to show the Raw Extracted Text and Classification logic. 
