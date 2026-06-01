import uuid


def test_rub_001_gateway_error_retains_balance(client, auth_production):
    user_before = client.get("/v1/users/me", headers=auth_production).json()
    balance_before = user_before["metered_balance"]

    res = client.post(
        "/v1/production/charges",
        headers=auth_production,
        json={"amount": 100.0, "metadata": {"simulate_gateway_error": "true"}}
    )
    assert res.status_code == 502

    user_after = client.get("/v1/users/me", headers=auth_production).json()
    assert user_after["metered_balance"] == balance_before


def test_rub_002_sandbox_cannot_mutate_production_tx(client, auth_sandbox, auth_production):
    prod_tx_id = "tx-prod-seed"

    client.post(
        "/v1/sandbox/checkout",
        headers=auth_sandbox,
        json={"simulation_ids": [prod_tx_id]}
    )

    tx = client.get(f"/v1/transactions/{prod_tx_id}", headers=auth_production).json()
    assert tx["status"] != "completed"


def test_rub_003_idempotency_scoped_per_user(client, auth_production, auth_production_secondary):
    key = f"ikey-{uuid.uuid4().hex}"

    res_a = client.post(
        "/v1/production/charges",
        headers={**auth_production, "X-Idempotency-Key": key},
        json={"amount": 50.0}
    ).json()

    res_b = client.post(
        "/v1/production/charges",
        headers={**auth_production_secondary, "X-Idempotency-Key": key},
        json={"amount": 75.0}
    ).json()

    assert res_b["transaction_id"] != res_a["transaction_id"]


def test_rub_004_production_happy_path_returns_201(client, auth_production):
    res = client.post(
        "/v1/production/charges",
        headers=auth_production,
        json={"amount": 10.0}
    )
    assert res.status_code == 201


def test_rub_005_sandbox_happy_path_returns_200(client, auth_sandbox):
    res = client.post(
        "/v1/sandbox/checkout",
        headers=auth_sandbox,
        json={"simulation_ids": ["sim-anything"]}
    )
    assert res.status_code == 200


def test_rub_006_metadata_marker_roundtrip(client, auth_production):
    marker = f"marker-{uuid.uuid4().hex}"
    created = client.post(
        "/v1/production/charges",
        headers=auth_production,
        json={"amount": 12.0, "metadata": {"sentinel": marker}}
    ).json()
    tx_id = created["transaction_id"]

    fetched = client.get(f"/v1/transactions/{tx_id}", headers=auth_production).json()
    assert fetched["metadata"]["sentinel"] == marker
