from sqlalchemy import BIGINT, BOOLEAN, VARCHAR, Column, LargeBinary, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.user import User
from src.infrastructure.models.base import mapper_registry, timestamp_columns
from src.infrastructure.models.session import Session

user = Table(
    "user",
    mapper_registry.metadata,
    Column("id", BIGINT, primary_key=True, default=generate_snowflake_id),
    Column("username", VARCHAR(32), nullable=False, unique=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column("public_bundle", JSONB, nullable=False),
    Column("vault", JSONB, nullable=False),
    Column("is_active", BOOLEAN, default=True),
    *timestamp_columns(),
)

def mapped_user_table():
    mapper_registry.map_imperatively(
        User,
        user,
        properties={
            "sessions": relationship(
                Session,
                back_populates="user",
                lazy="selectin",
                cascade="all, delete-orphan",
            ),
        },
    )
