# AI Usage Policy

## Status

This repository describes itself as an agentic AI prototype, but the current implementation does **not** call an external large language model or make probabilistic decisions. The agent is deterministic Python workflow code in `agent.py` and `tools.py`.

## Allowed use

AI assistance may be used to:

- Explore the repository and summarize existing behavior.
- Draft or review code, tests, documentation, and interface copy.
- Suggest implementation options and identify risks.
- Help debug local development failures using non-sensitive project data.

AI-generated changes must be reviewed by a developer before they are accepted. The reviewer is responsible for correctness, security, accessibility, privacy, and policy compliance.

## Prohibited use

Do not send real resident personal information, identity documents, income records, contact details, credentials, session tokens, database connection strings, or other confidential case data to an external AI service.

Do not use an AI system as the final decision-maker for eligibility, certificate authenticity, case status, benefit amount, denial, or other action that can materially affect a resident.

Do not present AI-generated summaries as verified facts without checking them against the source record.

## Human review requirements

The caseworker remains accountable for every consequential decision. The application must keep status changes behind the explicit approval flow, and a reviewer must check the underlying evidence before approving or rejecting a proposed status.

Certificate submission is not certificate verification. A submitted filename or document record must never be treated as proof of originality or issuing-authority confirmation.

## Data handling

The current demo uses mock data and, for browser uploads, stores document filenames rather than file contents. This is not an acceptable production evidence-storage design. Production work must establish data classification, consent and notice, retention/deletion rules, encryption, access logging, least-privilege access, and an approved service boundary before any AI feature handles resident information.

## Transparency

When AI services are introduced, record the service, model/version, purpose, data fields sent, retention behavior, human-review point, and known limitations. Users must be able to distinguish source evidence, deterministic checks, AI-generated suggestions, and human decisions.

## Incident and correction rule

If an AI-assisted output is wrong, unsupported, or exposes sensitive information, stop using the output, preserve the relevant audit information, correct the case through an authorized human workflow, and report the incident according to the organization’s privacy and security process.

## Current implementation note

No external AI dependency is present in `requirements.txt`. The present “agent” coordinates explicit checks and approval requests; it does not learn from cases, infer document contents, or autonomously decide resident outcomes.
