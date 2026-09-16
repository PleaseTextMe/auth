"""update_user_table

Revision ID: 3b0caad7918d
Revises: 98af8bb5b1d2
Create Date: 2026-08-04 22:30:22.679552

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3b0caad7918d'
down_revision: Union[str, Sequence[str], None] = '98af8bb5b1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('user', 'email', type_=sa.String(length=255))
    op.alter_column('user', 'auth_hash', type_=sa.String(length=255))
    op.alter_column('user', 'kdf_salt', type_=sa.String(length=64))


def downgrade() -> None:
    op.alter_column('user', 'kdf_salt', type_=sa.String())
    op.alter_column('user', 'auth_hash', type_=sa.String())
    op.alter_column('user', 'email', type_=sa.String())
