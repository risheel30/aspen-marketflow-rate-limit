from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    tier: str  # "sandbox" or "production"
    metered_balance: int

class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    status: str  # "pending", "completed", "failed"
    tier: str
    processed_at: datetime
    metadata: Dict[str, str] = Field(default_factory=dict)

USERS: Dict[str, UserProfile] = {}
TRANSACTIONS: Dict[str, Transaction] = {}
IDEMPOTENCY_CACHE: Dict[str, Dict] = {}


def reset_db():
    USERS.clear()
    USERS["usr-sandbox-99"] = UserProfile(user_id="usr-sandbox-99", tier="sandbox", metered_balance=1000)
    USERS["usr-prod-10"] = UserProfile(user_id="usr-prod-10", tier="production", metered_balance=10)
    USERS["usr-prod-20"] = UserProfile(user_id="usr-prod-20", tier="production", metered_balance=10)

    TRANSACTIONS.clear()
    TRANSACTIONS["tx-prod-seed"] = Transaction(
        id="tx-prod-seed",
        user_id="usr-prod-10",
        amount=150.0,
        status="pending",
        tier="production",
        processed_at=datetime(2026, 1, 1, 12, 0, 0),
        metadata={"environment": "production-live"}
    )

    IDEMPOTENCY_CACHE.clear()


reset_db()
