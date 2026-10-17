# Cloud Resource Attribution Agent

Local-first deterministic Python agent for attributing supplied cloud cost records to teams, projects, and environments using explicit tags. It does not connect to cloud accounts.

## Features
- JSON and CSV input.
- Required-field and cost validation.
- Explicit tag attribution; missing values become `unallocated`.
- Duplicate IDs and invalid rows are flagged.
- Totals stay separate by currency.
- Auditable JSON report; no cloud credentials or network calls.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m core.cli validate examples/cost_records.json
python -m core.cli attribute examples/cost_records.json --output attribution-report.json
python -m unittest discover -s tests -v
python verification/readiness_audit.py
```

Python 3.10+ is recommended. JSON input is a list of objects with `record_id`, `resource_id`, `service`, `cost`, `currency`, and `tags`. CSV uses those columns and a JSON-encoded `tags` cell.

## Limits
No AWS/Azure/GCP API or billing export is queried. The agent cannot verify invoice accuracy or tag ownership. Human review is required before showback, chargeback, or accounting use.
