# Decisions

This file records the important product and engineering choices made while building the Caseworker Morning prototype. It is intentionally written during implementation so the reasoning and tradeoffs remain visible.

## Purpose and boundary

The prototype automates repetitive evidence review while keeping consequential case-status changes behind explicit human approval. It is a demonstration system, not a benefits-decision system and not suitable for production resident data.

## What we chose

### Deterministic agent workflow

We chose a small Python `CaseworkerAgent` that calls explicit tools for case details, resident details, documents, eligibility, certificates, and status updates. This makes the workflow inspectable and predictable for a prototype.

### Human approval for status changes

The agent prepares a proposed status and reason, but does not change the case status until a caseworker approves it. Rejection records that the proposal was not executed. This is the central safety boundary because a status decision can affect a resident.

### Certificate state separate from required documents

We chose to track certificate presence and originality separately from the required-document count. A case can therefore show `3/3` required documents submitted while still requiring certificate verification.

### Pending verification instead of automatic originality

When a certificate is recorded, the system reports `Pending human verification` and leaves `original` false. A filename or upload action is evidence of submission, not proof that the document is authentic.

### Filename metadata for the demo

The browser upload controls send document names rather than file bytes. This keeps the demo small and avoids pretending that it has secure document storage or a real verification service.

### Backward-compatible existing-case correction

Existing cases may contain stale certificate state from before certificate upload was supported. We added an existing-case action that records the already-submitted certificate and persists the corrected state, rather than silently changing old records during every read.

### MongoDB when available, in-memory fallback otherwise

The application uses MongoDB when it can connect and otherwise runs with temporary in-memory dictionaries. This keeps local demonstration easy while making the persistence boundary explicit.

## What we rejected and why

### Automatic approval

Rejected because the system handles housing and other assistance cases. The agent may recommend a status, but it must not make the final consequential decision.

### Treating every uploaded filename as proof of authenticity

Rejected because submission, originality, and issuing-authority verification are different claims. The current workflow records submission and leaves authenticity for a human or future verification service.

### Adding certificates to the required-document total

Rejected because it would change the meaning of the existing `required` count and make old cases appear to have missing required documents. Certificates remain a separate review dimension.

### Silent data migration on page load

Rejected because a read operation should not invent evidence or rewrite a case without an explicit user action. The correction is exposed as a caseworker action and is audit logged.

### Building a real file-storage or OCR pipeline

Rejected for this prototype because it would add security, retention, malware-scanning, access-control, and operational requirements unrelated to demonstrating the approval workflow.

### Introducing an external LLM

Rejected because the current problem can be demonstrated with deterministic rules. An LLM would add cost, nondeterminism, privacy questions, and a larger evaluation burden without improving this narrow workflow.

## What we cut for time

- Real file upload storage and download/view controls.
- Document malware scanning, encryption, retention, and access policies.
- Issuing-authority API integration and certificate-reference lookup.
- A full eligibility rules engine and configurable policy administration.
- Multi-user identity, role-based access control, and session management beyond the demo login.
- Automated tests, browser end-to-end tests, and production deployment configuration.
- A complete audit-log viewer and immutable audit storage.

## What this solution does not do

- It does not determine legal eligibility or make a benefits decision.
- It does not verify that a certificate is genuine.
- It does not preserve uploaded file contents.
- It does not protect the demo credentials or provide production-grade authentication.
- It does not provide privacy, records-retention, accessibility, or regulatory compliance guarantees.
- It does not support concurrent editing or robust conflict resolution.
- It does not use a machine-learning model to infer facts from documents.

## What we would fix first

1. Replace filename-only evidence with secure object storage, malware scanning, access control, retention rules, and an evidence record containing provenance and timestamps.
2. Add real certificate verification through an issuing-authority integration, with clear failure and manual-review states.
3. Add automated API and browser tests for case creation, existing-case certificate submission, approval, rejection, authentication, and persistence.
4. Replace the demo login with an identity provider and least-privilege roles.
5. Define and test the eligibility policy with domain owners before allowing any operational use.
