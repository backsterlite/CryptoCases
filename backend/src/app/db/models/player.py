from beanie import Document, Indexed
from pydantic import Field, ConfigDict
from datetime import datetime, timezone
from decimal import Decimal

class PlayerStat(Document):
    """
    Player statistics for soft-pity and loose streak control.
    """
    user_id: int = Indexed(unique=True)
    fail_streak: int = Field(default=0, description="Number of consecutive spins without a rare drop")
    rtp_session: Decimal = Field(default=Decimal("0"), description="Accumulated RTP in this session")
    net_loss: Decimal = Field(default=Decimal("0"), description="Accumulated difference (stakes–winnings) in USDT")

    class Settings:
        name = "player_stats"

class CapPool(Document):
    """
    Payout reserve, statistical buffer and payout limit.
    Single document with _id="main".
    """
    id: str = Field(
        default="main",
        alias="_id",
        description="Fixed ID of the single reserve")       # always "main"
    balance: Decimal = Field(Decimal("0"),  description="Current Reserve Balance (USDT)")
    sigma_buffer: Decimal = Field(Decimal("0"), description="Recommended statistical buffer (4σ)")
    max_payout: Decimal = Field(Decimal("0"), description="Maximum one-time payout (USDT)")
    
    model_config = ConfigDict(populate_by_name=True)

    class Settings:
        name = "cap_pool"
    

class ServerSeed(Document):
    """
    Provably-Fair: commit/reveal seeds.
    """
    seed: str = Field(..., description="Server seed in hex format")
    hash: str = Field(..., description="SHA256 hex(seed)")
    owner_id: str = Field(..., description="user id who receive this hash")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    used: bool = Field(default=False)

    class Settings:
        name = "server_seeds"

class SpinLog(Document):
    """
    Log of each spin for analytics and A/B tests.
    """
    user_id: int
    case_id: str
    server_seed_id: str
    server_seed_hash: str
    server_seed_seed: str
    client_seed: str
    nonce: int
    hmac_value: bytes
    raw_roll: Decimal
    table_id: str
    odds_version: str
    case_tier: str
    prize_id: str
    stake: Decimal
    payout: Decimal
    payout_usd: Decimal
    pity_before: Decimal
    pity_after: Decimal
    rtp_session: Decimal
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "spin_logs"