# ScopeCraft — Proposal Studio

A proposal-building portfolio application for freelancers and agencies: turn a brief and deliverables into an itemized estimate, milestones, exclusions and a reviewable document.

## Current application

The supported application is the root `main.py` and `static/` directory. Run:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. Render: Python runtime, repository root, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Health endpoint: `/health`. Dockerfile is included. No database, local model, paid service or API key is required for the default workflow.

## Implemented

- Responsive desktop and mobile workspace with fictional examples.
- Validated server-side document generation through `/api/proposal`.
- Browser-local saved records, explicit approval, reviewer notes and revision numbers.
- Markdown export, JSON backup/restore with duplicate-ID handling, and browser Print / Save PDF.
- Optional protected Gemini summary, with schema checks and provider failure handling.
- Content Security Policy, escaped rendered text and no external scripts/fonts.
- Automated backend tests and JavaScript syntax checks in GitHub Actions.

## Storage and privacy

Completed documents are stored in **this browser's localStorage**, not in a shared server database. They survive page reloads and server redeploys while browser data remains intact. They are not synced across browsers or devices. Clearing browser data removes them: export JSON backups to preserve or transfer work. Keep only public or fictional inputs in this public demo. The template API processes inputs but does not persist them server-side. Optional AI sends the supplied brief to Google only when explicitly requested with a valid access token.

Maximum 50 saved documents, 2 MB import limit. Backups are user-managed documents, not signed or tamper-proof audit logs. Approval is a local review status: no emails, payments, legal signatures or external actions occur.

## Optional AI configuration

Set `GEMINI_API_KEY` and a unique `AI_ACCESS_TOKEN` of at least 24 characters privately in the hosting environment. Optionally set `GEMINI_MODEL` (default `gemini-2.5-flash`). Never commit real values. Use the **Optional AI summary** button and enter the access token, not the model API key. The browser does not persist that token. Without configuration, the app returns a clear unavailable message and keeps the existing draft intact.

AI only adds a draft summary; it does not change source excerpts, prices or deliverable estimates. AI summaries need verification. The process-level cap is 10 AI calls per hour and resets on restart; this is not a distributed quota system. Use provider-level budgets before sharing access widely. Hosted real-provider responses have not been validated without private credentials; tests use a fake provider.

## Verification

13 backend tests cover normal generation, invalid inputs, optional-AI authentication, provider failure and rate limiting. Browser verification and deployment links are recorded in `UPWORK.md` after release.

## Portfolio scope

This is a functional portfolio workflow, not a production multi-tenant SaaS. Production deployment would add account authentication, durable server storage, role-based access, distributed limits, encrypted backups, monitoring and operational validation.

Estimates use Decimal arithmetic and round each line to two decimal places before summing. Totals are before tax. Milestones and assumptions are templates, not delivery guarantees.
