from sqlalchemy import BIGINT, BOOLEAN, VARCHAR, Column, String, Table

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.user import User
from src.infrastructure.models.base import mapper_registry, timestamp_columns

user = Table(
    "user",
    mapper_registry.metadata,
    Column("id", BIGINT, primary_key=True, default=generate_snowflake_id),
    Column("username", VARCHAR(32), nullable=False, unique=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("auth_hash", String(255), nullable=False),
    Column("is_active", BOOLEAN, default=True),
    Column("kdf_salt", String(64), nullable=False),
    *timestamp_columns(),
)

def mapped_user_table():
    mapper_registry.map_imperatively(User, user)
