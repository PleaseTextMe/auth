from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    Column,
    ForeignKey,
    LargeBinary,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.session import Session
from src.infrastructure.models.base import mapper_registry, timestamp_columns
from src.infrastructure.models.user import User

session = Table(
    "session",
    mapper_registry.metadata,
    Column("id", BIGINT, primary_key=True, default=generate_snowflake_id),
    Column(
        "user_id",
        BIGINT,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("user_agent", String(255), nullable=False),
    Column("auth_token_hash", LargeBinary, nullable=False),
    Column("user_ip", String(255)),
    Column("is_active", BOOLEAN, default=True),
    Column("device_type", String(255), default="other"),
    *timestamp_columns(),
)


def mapped_session_table():
    mapper_registry.map_imperatively(
        Session,
        session,
        properties={
            "user": relationship(
                User,
                back_populates="sessions",
                lazy="selectin",
            ),
        },
    )
