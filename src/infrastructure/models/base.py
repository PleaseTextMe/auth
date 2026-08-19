from sqlalchemy import Column, DateTime
from sqlalchemy.orm import registry

from src.core.utils.datetime import get_utc_now

mapper_registry = registry()


def timestamp_columns():
    return [
        Column(
            "created_at",
            DateTime,
            nullable=False,
            default=get_utc_now
        ),
        Column(
            "updated_at",
            DateTime,
            nullable=False,
            default=get_utc_now,
            onupdate=get_utc_now,
        ),
    ]
