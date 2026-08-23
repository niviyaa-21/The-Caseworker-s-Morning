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
6. **Simple dashboard** – a caseworker can run the agent and approve/reject the proposed action.
7. **Morning triage** – run read-only checks across the whole pending queue and sort findings by priority.
8. **Live queue state** – the dashboard updates case status and exposes pending approval requests through the API.
9. **Certificate verification** – each case is checked for certificate presence and whether its issuing reference appears original.

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
