# aspen-marketflow-rate-limit

Substrate for the `aspen__marketflow_rate_limit_001` Aspen test authoring task.
Small FastAPI metered payment gateway with two tiers (production and sandbox),
an in-memory idempotency cache, and a transaction store.

## Layout

- `marketflow/` FastAPI service (routes, models, in-memory stores)
- `tests/conftest.py` pytest fixtures (`client`, `auth_sandbox`, `auth_production`, `auth_production_secondary`)
- `tests/test_smoke.py` happy-path coverage of the legitimate developer flow

## Run smoke tests locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/test_smoke.py -q
```
