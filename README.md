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

## Example call

```
Agent:  Which store location are you calling about?
Caller: Hannah, store 31. Our bill went up during the outage.
Agent:  What's the store's ZIP code?
Caller: 98101
Agent:  [calls get_store_billing] Thanks, Hannah, that's verified for store 31 in Seattle.
        The bill went from about $611 to $790. The main driver is an 11 GB backup
        wireless overage during the November 14 to 16 fiber outage, about $165 plus
        $14 in fees. That overage is credit eligible. Want me to log a credit request?
Caller: Yes, please log it.
Agent:  [calls log_escalation] Done. Ticket TEL-7373E5. The telecom team responds
        within two business days.
```

## Test scenarios

| Store | ZIP | Scenario | Expected behavior |
| --- | --- | --- | --- |
| 12 | 75201 | Bill up $223 | Explains promo ending, one time technician visit, and next month estimate |
| 23 | 30303 | Savings check | Flags two lines unused for 94 days, about $768 a year |
| 31 | 98101 | Outage overage | Explains overage and logs a credit request ticket |
| 12 | 90210 | Wrong ZIP | API returns 403, agent shares nothing |

## Repo contents

| Path | What it is |
| --- | --- |
| `main.py` | FastAPI billing API with mock data |
| `agent/system_prompt.md` | Agent first message and system prompt |
| `agent/tools.md` | Webhook tool definitions |
| `agent/knowledge_base_billing_guide.md` | Knowledge base document uploaded to the agent |
| `render.yaml` | One click deploy config |

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

Live: https://coastline-billing-api.onrender.com

## Production notes

This is a demo. In production:
- Escalations would write to the client's ticketing system (Zendesk, ServiceNow) instead of memory
- Billing data would come from a telecom expense management platform or parsed carrier invoices
- Verification would use a stronger factor than ZIP code, such as a callback or SSO identity

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
