# Course-Agent: Autonomous Discovery of CMU Course Calendars

This repository contains an **agentic AI system** that autonomously discovers
official Carnegie Mellon University course websites and extracts embedded
Google Calendar (iCal) information when available. It is a multi-agent architecture where one agent proposes candidate course websites and a separate critic agent independently evaluates the decision, vetoing weak or ambiguous verifications before any data is committed.

The system operates under uncertainty:
- No predefined list of course website domains
- Some courses have no public websites
- Some websites do not publish calendars

To handle this, we model discovery as a **probabilistic, auditable agent workflow**
rather than a deterministic scraper.

---

## 🎯 Goals

For each CMU course:
1. Discover candidate course websites using web search
2. Verify which (if any) site is the official course website
3. Detect embedded Google Calendars via HTML iframe inspection
4. Persist all results, including failures, to Supabase for auditing and review

---

## 💭 Why Agentic AI?

This task requires:
- Search under uncertainty
- Semantic relevance judgment
- Conditional branching
- Tool orchestration
- Graceful failure handling

A single script is brittle, while an agent can **observe → decide → act → record**.

---

## 🏗 Architecture Overview
To visualize LangGraph, run `python -m course_agent.scripts.visualize_graph` in root directory, then paste the content into [https://mermaid.live](https://mermaid.live).

---

## 🗃 Data Model (Supabase)

- `courses`: canonical course data (input)
- `course_websites`: discovered candidate websites + confidence
- `calendar_sources`: extracted calendar artifacts
- `agent_runs`: metadata for reproducibility and auditing

Agent outputs are treated as **hypotheses**, not ground truth.

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env.development`
```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...

OPENAI_API_KEY=...
SEARCH_API_KEY=...
```

### 3. Run the command in the root directory in cmucal-backend
`python -m course_agent.scripts.run_all_courses`


## Trouble shooting
- If encounter `postgrest.exceptions.APIError: {'message': 'permission denied for table agent_runs', 'code': '42501', 'hint': None, 'details': None}`, run the following query in Supabase's SQL Editor
    - `GRANT ALL PRIVILEGES ON TABLE agent_runs TO service_role;`
