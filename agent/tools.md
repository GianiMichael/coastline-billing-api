# Webhook tools

Both tools call the API in this repo, deployed at `https://coastline-billing-api.onrender.com`.

## get_store_billing

| Field | Value |
| --- | --- |
| Method | GET |
| URL | `https://coastline-billing-api.onrender.com/stores/{store_number}` |
| Description | Looks up a store's current telecom billing. Call only after the caller gives both their store number and ZIP code. Returns totals, what changed, unused lines, and savings. A 403 error means the ZIP did not match. |

| Parameter | Location | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `store_number` | path | string | yes | The store number the caller gives, digits only, for example 12 |
| `zip` | query | string | yes | The 5 digit ZIP code the caller gives for the store |

## log_escalation

| Field | Value |
| --- | --- |
| Method | POST |
| URL | `https://coastline-billing-api.onrender.com/escalations` |
| Description | Logs a ticket for the telecom team. Use for disputes, credit requests, or anything you cannot resolve. Returns a ticket ID to read to the caller. |

Body (JSON):

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `store_number` | string | yes | The store number |
| `caller_name` | string | yes | The caller's name |
| `issue_summary` | string | yes | One sentence summary of the issue |
| `amount_in_question` | number | no | Dollar amount in dispute, if any |
