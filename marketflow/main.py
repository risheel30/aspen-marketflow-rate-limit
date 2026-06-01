import uuid
from fastapi import FastAPI, Header, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from marketflow.models import USERS, TRANSACTIONS, IDEMPOTENCY_CACHE, Transaction, UserProfile

app = FastAPI(title="MarketFlow Gateway Engine")


class ChargeRequest(BaseModel):
    amount: float
    metadata: Optional[Dict[str, str]] = None


class SandboxCheckoutRequest(BaseModel):
    simulation_ids: List[str]


def get_current_user(x_user_id: Optional[str] = Header(None)):
    if not x_user_id or x_user_id not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials"
        )
    return USERS[x_user_id]


@app.post("/v1/production/charges", status_code=201)
def create_production_charge(
    payload: ChargeRequest,
    user: UserProfile = Depends(get_current_user),
    x_idempotency_key: Optional[str] = Header(None)
):
    if user.tier != "production":
        raise HTTPException(status_code=403, detail="Operation restricted to production accounts")

    if user.metered_balance <= 0:
        raise HTTPException(status_code=429, detail="Metered volume quota exhausted")

    if x_idempotency_key and x_idempotency_key in IDEMPOTENCY_CACHE:
        cached = IDEMPOTENCY_CACHE[x_idempotency_key]
        return cached["response_body"]

    user.metered_balance -= 1

    if payload.metadata and payload.metadata.get("simulate_gateway_error") == "true":
        raise HTTPException(status_code=502, detail="Bad Gateway response from intermediate merchant mesh")

    tx_id = f"tx-live-{uuid.uuid4().hex[:8]}"
    new_tx = Transaction(
        id=tx_id,
        user_id=user.user_id,
        amount=payload.amount,
        status="completed",
        tier="production",
        processed_at=datetime.utcnow(),
        metadata=payload.metadata or {}
    )
    TRANSACTIONS[tx_id] = new_tx

    res = {
        "transaction_id": tx_id,
        "amount": payload.amount,
        "status": "completed",
        "processed_at": new_tx.processed_at.isoformat()
    }

    if x_idempotency_key:
        IDEMPOTENCY_CACHE[x_idempotency_key] = {"transaction_id": tx_id, "response_body": res}

    return res


@app.post("/v1/sandbox/checkout")
def sandbox_checkout(
    payload: SandboxCheckoutRequest,
    user: UserProfile = Depends(get_current_user)
):
    if user.tier != "sandbox":
        raise HTTPException(status_code=403, detail="Operation restricted to sandbox test footprints")

    processed = []
    for tid in payload.simulation_ids:
        if tid in TRANSACTIONS:
            target_tx = TRANSACTIONS[tid]
            target_tx.status = "completed"
            processed.append(tid)

    return {"status": "processed", "applied_simulations": processed}


@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str, user: UserProfile = Depends(get_current_user)):
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(status_code=404, detail="Transaction artifact not uncovered")
    tx = TRANSACTIONS[transaction_id]
    if tx.user_id != user.user_id and user.user_id != "usr-admin-system":
        raise HTTPException(status_code=403, detail="Unauthorized resource visibility boundary break")
    return tx


@app.get("/v1/users/me")
def get_me(user: UserProfile = Depends(get_current_user)):
    return user
