# Coastline Billing API

Backend for a voice AI agent, built on ElevenLabs ElevenAgents, that answers telecom billing questions for a multi location retailer.

## The problem

Retailers with dozens of locations pay hundreds of telecom invoices a month across several carriers. Store managers and finance staff see a bill go up and have no quick way to find out why. Questions pile up with a small telecom team, and unused lines keep billing for months because nobody notices them.

## The solution

A voice agent that store staff can call any time. It:

1. Verifies the caller by store number and ZIP code
2. Pulls that store's live billing data through this API
3. Explains in plain language why the bill changed (promotions ending, one time charges, usage overages)
4. Flags unused lines and the savings from disconnecting them
5. Logs an escalation ticket for the telecom team when a dispute or credit request is needed

All data in this repo is fictional.

## Architecture

```
Caller (voice) → ElevenLabs agent (prompt + knowledge base)
                      │
                      ├── get_store_billing  → GET  /stores/{store_number}?zip=
                      └── log_escalation     → POST /escalations
```

- **Knowledge base:** billing policies, line item definitions, and escalation rules
- **This API:** store level billing data and ticket logging
- **Verification is enforced server side.** A wrong ZIP returns 403, so the agent cannot share billing data even if the conversation goes off script.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Health check |
| GET | `/stores/{store_number}?zip=XXXXX` | Verified billing lookup: totals, changes, unused lines, savings |
| POST | `/escalations` | Log a ticket: store_number, caller_name, issue_summary, amount_in_question |
| GET | `/escalations` | List logged tickets |

Example:

```
GET /stores/12?zip=75201
→ November total $841, up $223: promo ended ($40), technician visit ($150), fees ($33)
```

## Run locally

```
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive API docs.

## Deploy

`render.yaml` deploys this as a free web service on Render (New → Blueprint).

## Built with

Python, FastAPI, ElevenLabs ElevenAgents, Render
