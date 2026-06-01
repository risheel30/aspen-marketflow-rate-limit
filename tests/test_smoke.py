def test_smoke_production_charge_happy_path(client, auth_production):
    response = client.post(
        "/v1/production/charges",
        headers=auth_production,
        json={"amount": 49.99, "metadata": {"origin": "web"}}
    )
    assert response.status_code == 201
    data = response.json()
    assert "transaction_id" in data
    assert data["status"] == "completed"


def test_smoke_sandbox_flow(client, auth_sandbox):
    response = client.post(
        "/v1/sandbox/checkout",
        headers=auth_sandbox,
        json={"simulation_ids": ["sim-123", "sim-456"]}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"


def test_smoke_get_my_transaction(client, auth_production):
    created = client.post(
        "/v1/production/charges",
        headers=auth_production,
        json={"amount": 10.0}
    ).json()
    tx_id = created["transaction_id"]
    res = client.get(f"/v1/transactions/{tx_id}", headers=auth_production)
    assert res.status_code == 200


def test_smoke_user_profile_visible(client, auth_production):
    res = client.get("/v1/users/me", headers=auth_production)
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == "usr-prod-10"
    assert body["tier"] == "production"
