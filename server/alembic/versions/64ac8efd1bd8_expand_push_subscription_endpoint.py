"""Expand push subscription endpoint

Revision ID: 64ac8efd1bd8
Revises: 18329158e509
Create Date: 2026-08-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '64ac8efd1bd8'
down_revision: Union[str, Sequence[str], None] = '18329158e509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  with op.batch_alter_table('push_subscriptions') as batch_op:
    batch_op.alter_column(
      'endpoint',
      existing_type=sa.String(length=255),
      type_=sa.String(length=512),
      existing_nullable=False,
    )


def downgrade() -> None:
  with op.batch_alter_table('push_subscriptions') as batch_op:
    batch_op.alter_column(
      'endpoint',
      existing_type=sa.String(length=512),
      type_=sa.String(length=255),
      existing_nullable=False,
    )
