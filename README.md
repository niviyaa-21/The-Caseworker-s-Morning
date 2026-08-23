# Caseworker Morning Assistant

A small **Agentic AI + Human-in-the-Loop** prototype for Problem 5: **The Caseworker's Morning**.

## 1. Problem

A caseworker spends a large part of every morning repeating the same sequence of clicks:

- Open a case
- Read resident information
- Check submitted documents
- Check eligibility
- Prepare the next action
- Update the case
- Record what happened

The goal is to automate the repetitive part with an agent while keeping a human in control of high-impact actions.

## 2. What this prototype demonstrates

This project implements:

1. **Agent workflow** – coordinates several tools in sequence.
2. **Tool calling** – the agent calls functions for case, resident, document and eligibility data.
3. **Risk-aware execution** – read-only actions happen automatically.
4. **Human approval** – changing a case status requires explicit approval.
5. **Audit logging** – important actions are recorded.
6. **Operations dashboard** – the overview shows total, pending, needs-attention, and completed case counts, a completion chart, recent cases, and the audit log.
7. **Morning triage** – run read-only checks across the whole pending queue and sort findings by priority.
8. **Live queue state** – the dashboard updates case status and exposes pending approval requests through the API.
9. **Certificate verification** – each case is checked for certificate presence and whether its issuing reference appears original.
10. **All-cases register** – a separate dashboard tab lists every case with its resident, program, status, and review action.
11. **Dedicated case view** – selecting a case opens its evidence and approval workflow in a new browser tab.
12. **Case creation** – authorized dashboard users can create a pending case from a modal, select a benefit program, complete program-specific fields, and mark documents as submitted.
13. **Program requirements** – a predefined requirements registry determines the fields and documents shown for each benefit program.
14. **Restricted access** – the dashboard and APIs require the caseworker login.
15. **MongoDB persistence** – case, resident, evidence, and audit data are stored in MongoDB when configured.

> This is a demonstration system using mock data. It is not suitable for real benefits decisions or production use.

## 3. Architecture

```text
                  ┌──────────────────────┐
                  │    Caseworker UI     │
                  │       React/HTML     │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │      Flask API       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Caseworker Agent   │
                  │  workflow + guardrail│
                  └──────────┬───────────┘
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
       Case Tool       Document Tool    Eligibility Tool
             │               │                │
             └───────────────┼────────────────┘
                             ▼
                    Human Approval Gate
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
                 Approve            Reject
                    │                 │
                    ▼                 ▼
              Update Case         Do Nothing
                    │
                    ▼
                 Audit Log
```

## 4. Why the human approval step matters

The agent is allowed to inspect information automatically.

However, an action such as changing an important case status can have consequences for a resident. Therefore the agent creates an approval request instead of executing the action immediately.

The flow is:

```text
Agent detects required action
          ↓
Agent explains the reason
          ↓
Human approval required
       ↙       ↘
   Approve     Reject
      ↓           ↓
 Execute       Stop
```

This is the core **guardrail** in the project.

## 5. Project structure

```text
caseworker_agent/
│
├── app.py                 # Flask API and routes
├── agent.py               # Agent workflow and approval logic
├── tools.py               # Mock external-system tools
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html         # Caseworker dashboard
│
└── static/
    └── style.css          # Dashboard styling
```

## 6. Run locally

### Step 1 – Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2 – Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 – Start the application

```bash
python app.py
```

### Step 4 – Open the dashboard

Open:

```text
http://127.0.0.1:5000
```

## 7. How to demonstrate it

### Configure MongoDB and login

Install and run MongoDB locally, or provide a MongoDB Atlas connection string. Set these environment variables before starting the app:

```powershell
$env:MONGO_URI = "mongodb://127.0.0.1:27017"
$env:MONGO_DB = "caseworker_morning"
$env:FLASK_SECRET_KEY = "replace-with-a-long-random-value"
$env:CASEWORKER_USERNAME = "caseworker"
$env:CASEWORKER_PASSWORD = "replace-with-a-strong-password"
python app.py
```

The database and collections are created automatically on first successful connection. The initial demo data is seeded only when the database has no cases. If MongoDB is unavailable, the app reports the database as unavailable and uses temporary in-memory data for development; do not use that mode for real resident data.

### Demo 1 – Successful case

Select **Case #1001**.

The agent automatically:

- Reads the case
- Reads resident information
- Checks documents
- Checks eligibility
- Proposes `ready_for_review`

The agent then stops and displays:

> Human approval required.

Click **Approve**.

The case status changes.

### Demo 2 – Incomplete documents

Select **Case #1002**.

The agent discovers that only 2 of 3 documents were submitted.

It proposes:

```text
needs_attention
```

The caseworker can decide whether to approve the proposed status update.

### Demo 3 – Failed eligibility

Select **Case #1003**.

The eligibility check fails.

The agent explains the reason and proposes:

```text
needs_attention
```

Again, the actual status change is protected by the approval gate.

## 8. API endpoints

### Run the agent

```http
POST /api/run
Content-Type: application/json

{
  "case_id": "1001"
}
```

### Approve or reject an action

```http
POST /api/approval
Content-Type: application/json

{
  "approval_id": "APR-1001",
  "approved": true
}
```

Set `approved` to `false` to reject.

### View audit logs

```http
GET /api/logs
```

### Run morning triage

```http
POST /api/triage
```

This checks every case with `pending` status and returns a recommendation, priority, evidence summary, and pending approval list.

Certificate results include `present`, `original`, `verification_method`, and an explanation. A missing or unverified certificate prevents the agent from recommending `ready_for_review`.

### View live cases and approvals

```http
GET /api/cases
GET /api/approvals
```

### Create a case

```http
POST /api/cases
Content-Type: application/json

{
      "name": "Sam Taylor",
      "program": "Transport Assistance",
      "language": "English",
      "contact": "sam@example.test"
}
```

New cases begin with `pending` status and no submitted documents or verified certificate.

The dashboard Create case modal loads requirements from `GET /api/program-requirements`. Selecting a file marks that document as submitted in this demo; production deployments should replace that behavior with secure file storage and document scanning.

Approval payloads must contain a real JSON boolean for `approved`; invalid requests are rejected with `400`.

## 9. How to turn this into a real AI agent

The current prototype uses deterministic Python logic so it can run without an API key.

For a stronger hackathon version, replace the decision logic with an LLM-based agent.

Possible architecture:

```text
                    LLM
                     │
              decides next tool
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Case API      Document API   Eligibility API
       │             │             │
       └─────────────┼─────────────┘
                     ▼
               Agent observes
                     │
                     ▼
             Next tool / finish
```

The LLM should **not** directly modify databases.

Instead:

```text
LLM → tool request → backend guardrail → tool execution
```

The backend should enforce the permission rules.

## 10. Recommended guardrail policy

| Action | Risk | Agent allowed? |
|---|---|---|
| Read case | Low | Yes |
| Read resident data | Low | Yes |
| Read documents | Low | Yes |
| Check eligibility | Low | Yes |
| Generate summary | Low | Yes |
| Prepare status update | Medium | Yes, but do not submit |
| Change case status | High | Human approval |
| Delete case | Critical | Human approval / restricted |
| Send official decision | High | Human approval |
| Change benefit amount | Critical | Human approval |

## 11. Production improvements

For a real implementation, add:

- Authentication and role-based access control
- PostgreSQL or another production database
- Real REST APIs instead of mock functions
- LLM tool calling
- Structured tool schemas
- Approval expiry
- Idempotency keys
- Retry and timeout handling
- API rate limiting
- Encryption
- PII protection
- Full audit trail
- Prompt-injection protection
- Model output validation
- Human override
- Monitoring and alerting
- Automated tests
- Docker deployment

## 12. Important design principle

The most important principle is:

> **The AI can recommend and automate routine work, but the system—not the model—enforces what the AI is allowed to do.**

This makes the project a demonstration of **Agentic AI + Human-in-the-Loop + Guardrails**, rather than just an AI chatbot.
