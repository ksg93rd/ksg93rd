# Architecture reconstruction and the isometric map

## What to identify

Only components with actual source evidence:

users · browser clients · mobile clients · desktop clients · frontend applications · APIs · gateways · backend services · serverless functions · workers · schedulers · queues · databases · caches · storage · authentication providers · authorization services · AI/model providers · payment providers · messaging systems · external SaaS · monitoring · analytics · deployment systems · build systems · container infrastructure

## Component evidence model

Every component gets an ID (`N001`, `N002`, …) and records:

| Field | Notes |
| --- | --- |
| ID | `N###` |
| Name | As it appears in the codebase |
| Type | Frontend, API, worker, database, external provider… |
| Responsibility | What it actually does |
| Execution environment | Browser, Node, edge, container, managed service |
| Entry point | File and symbol |
| Inputs / Outputs | Real ones, from source |
| Dependencies | Internal and external |
| Authentication | How it authenticates or is authenticated |
| Storage | What it persists |
| External services | Verified destinations |
| Evidence | File citations |
| Confidence | See below |

### Confidence levels

- **CONFIRMED** — direct evidence in source.
- **STRONGLY INFERRED** — multiple independent repository indicators.
- **UNVERIFIED** — insufficient evidence.

## Connection evidence model

Every significant edge gets an ID (`E001`, `E002`, …) and records: source · destination · direction · protocol · operation · triggering event · payload type · authentication · source file · destination implementation · confidence.

## Path categories

Classify every path; never merge fundamentally different types into one unlabeled arrow.

| Category | Covers |
| --- | --- |
| `CONTROL` | Requests, routing, invocation, orchestration |
| `DATA` | Application data movement |
| `AUTH` | Authentication and authorization |
| `EVENT` | Webhooks, queues, events, async processing |
| `BUILD` | Compilation and packaging |
| `DEPLOYMENT` | Release and deployment infrastructure |
| `SECURITY` | Observed suspicious or malicious behavior |

## Trace real runtime flows

Trace major workflows end to end, for example:

```
USER → FRONTEND → API → AUTH → SERVICE → DATABASE
CLIENT → EDGE FUNCTION → AI PROVIDER → DATABASE → CLIENT
PAYMENT PROVIDER → WEBHOOK → SERVICE → DATABASE
UPLOAD → STORAGE → PROCESSOR → AI SERVICE → DATABASE → UI
```

Represent only flows the evidence supports.

## Payload labeling

Label payloads only when directly supported by source — `POST /api/chat`, `JWT`, `multipart/form-data`, `WebhookEvent`, `ChatRequest`, `conversation_id`, `embedding[]`, `SQL result`, `JSON`.

Do not invent schemas. When unknown, write `PAYLOAD NOT VERIFIED`.

## Trust boundaries

Identify where applicable: public internet · authenticated user boundary · frontend/backend boundary · privileged admin boundary · database boundary · cloud boundary · AI provider boundary · third-party SaaS boundary · payment boundary · CI/CD boundary · developer workstation boundary.

Call out explicitly where sensitive data crosses a boundary.

## The isometric system map

`docs/architecture/system-map.html` — an interactive isometric visualization. Infrastructure uses varied 3D structures so type is readable at a glance:

| Component | Structure |
| --- | --- |
| User / client | Workstation, device |
| Frontend | Office building |
| API | Service tower |
| Serverless | Compute pod |
| Database | Data center |
| Storage | Warehouse |
| Authentication | Security checkpoint |
| AI provider | Compute facility |
| Queue | Logistics hub |
| External SaaS | Partner facility |
| Monitoring | Operations center |
| CI/CD | Build factory |

**Visual beauty must never override technical truth.**

### Layout

- **Left** — users, browsers, external clients
- **Center-left** — frontend / application layer
- **Center** — APIs, orchestration, business services
- **Center-right** — databases, storage, workers, queues, AI
- **Right** — external providers
- **Top / background** — build, deployment, CI/CD, administration, monitoring

### Layers

Separately toggleable:

`NORMAL ARCHITECTURE` · `CONTROL PATHS` · `DATA PATHS` · `AUTH PATHS` · `EVENT PATHS` · `BUILD/DEPLOY PATHS` · `SECURITY FINDINGS`

**Never render suspected malicious traffic as if it were normal architecture.**

### Interaction

Where HTML/SVG capability exists: zoom · pan · layer toggles · architecture/security toggle · path-type filters · severity filters · confidence filters · node search · hover summaries · click-for-evidence · evidence drawer/panel · focus mode · legend · responsive layout · keyboard accessibility · readable labels.

Do not rely on color alone to communicate security state — pair it with icons, patterns, line styles, and text labels.

### Visual states

Visually distinguish: Confirmed Normal · Strongly Inferred · Unverified · Vulnerable · Suspicious · Highly Suspicious · Malicious Confirmed.

## Explainer panel

Include these sections:

`SYSTEM PURPOSE` · `ARCHITECTURE AT A GLANCE` · `MAJOR COMPONENTS` · `CRITICAL RUNTIME FLOWS` · `CONTROL PLANE` · `DATA PLANE` · `AUTHENTICATION & AUTHORIZATION` · `TRUST BOUNDARIES` · `EXTERNAL DEPENDENCIES` · `SUPPLY-CHAIN POSTURE` · `SECURITY FINDINGS` · `PROMPT-INJECTION FINDINGS` · `MALWARE ASSESSMENT` · `ARCHITECTURAL RISKS` · `UNKNOWNS` · `RESIDUAL RISK`
