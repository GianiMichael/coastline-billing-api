"""Coastline Retail telecom billing API (mock data).

Two endpoints for the ElevenLabs voice agent:
  GET  /stores/{store_number}?zip=XXXXX  verified billing lookup
  POST /escalations                      log a ticket for the telecom team
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Coastline Telecom Billing API")

STANDARD_LINES = [
    {"service": "Business internet 500 Mbps", "carrier": "Brightline Fiber", "monthly": 189},
    {"service": "Backup wireless internet", "carrier": "Summit Wireless", "monthly": 45},
    {"service": "Cloud voice lines (4)", "carrier": "Brightline Voice", "monthly": 128},
    {"service": "Point of sale data line", "carrier": "Brightline Fiber", "monthly": 60},
    {"service": "Manager mobile lines (2)", "carrier": "Summit Wireless", "monthly": 110},
]

STORES = {
    "7": {"city": "Phoenix, AZ", "zip": "85016", "manager": "Dana Ruiz",
          "october_total": 612, "november_total": 609, "changes": [], "unused_lines": []},
    "12": {"city": "Dallas, TX", "zip": "75201", "manager": "Marcus Lee",
           "october_total": 618, "november_total": 841,
           "changes": [
               {"item": "Internet promotional discount ended Nov 1", "type": "recurring", "amount": 40},
               {"item": "Technician visit Nov 9 to replace failed router", "type": "one time", "amount": 150},
               {"item": "Taxes and fees on new charges", "type": "fees", "amount": 33},
           ],
           "expected_next_month": 660, "unused_lines": []},
    "18": {"city": "Denver, CO", "zip": "80202", "manager": "Priya Shah",
           "october_total": 604, "november_total": 607, "changes": [], "unused_lines": []},
    "23": {"city": "Atlanta, GA", "zip": "30303", "manager": "Kevin Brooks",
           "october_total": 702, "november_total": 705, "changes": [],
           "unused_lines": [
               {"line": "ending 4471", "days_without_calls": 94, "monthly": 32},
               {"line": "ending 4472", "days_without_calls": 94, "monthly": 32},
           ]},
    "31": {"city": "Seattle, WA", "zip": "98101", "manager": "Hannah Ortiz",
           "october_total": 611, "november_total": 790,
           "changes": [
               {"item": "Backup wireless data overage, 11 GB during fiber outage Nov 14 to 16",
                "type": "usage", "amount": 165, "credit_possible": True},
               {"item": "Taxes and fees on overage", "type": "fees", "amount": 14},
           ],
           "unused_lines": []},
    "40": {"city": "Miami, FL", "zip": "33131", "manager": "Luis Fernandez",
           "october_total": 598, "november_total": 601, "changes": [], "unused_lines": []},
}

ESCALATIONS: list[dict] = []


@app.get("/")
def health():
    return {"status": "ok", "stores": len(STORES)}


@app.get("/stores/{store_number}")
def get_store_billing(store_number: str, zip: str):
    store = STORES.get(store_number.strip().lstrip("0"))
    if store is None:
        raise HTTPException(404, detail="Store not found. Ask the caller to confirm the store number.")
    if zip.strip() != store["zip"]:
        raise HTTPException(403, detail="ZIP code does not match. Do not share billing details.")

    unused = store["unused_lines"]
    monthly_savings = sum(line["monthly"] for line in unused)
    return {
        "verified": True,
        "store_number": store_number,
        "city": store["city"],
        "manager": store["manager"],
        "october_total": store["october_total"],
        "november_total": store["november_total"],
        "change_from_last_month": store["november_total"] - store["october_total"],
        "changes": store["changes"],
        "expected_next_month": store.get("expected_next_month"),
        "standard_services": STANDARD_LINES,
        "unused_lines": unused,
        "potential_savings": {"monthly": monthly_savings, "annual": monthly_savings * 12},
    }


class Escalation(BaseModel):
    store_number: str
    caller_name: str
    issue_summary: str
    amount_in_question: float | None = None


@app.post("/escalations")
def log_escalation(req: Escalation):
    ticket = {
        "ticket_id": "TEL-" + uuid4().hex[:6].upper(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **req.model_dump(),
        "response_time": "2 business days",
    }
    ESCALATIONS.append(ticket)
    return ticket


@app.get("/escalations")
def list_escalations():
    return ESCALATIONS
