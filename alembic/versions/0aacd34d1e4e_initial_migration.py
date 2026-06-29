"""Initial migration

Revision ID: 0aacd34d1e4e
Revises: 
Create Date: 2026-06-29 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = '0aacd34d1e4e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'payments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('meta', JSON, nullable=False, server_default='{}'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('idempotency_key', sa.String(50), nullable=False, unique=True),
        sa.Column('webhook_url', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime, nullable=True),
    )
    
    op.create_index('idx_payments_idempotency_key', 'payments', ['idempotency_key'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    
    op.create_table(
        'outbox',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('aggregate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('payload', JSON, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
    )
    
    op.create_index('idx_outbox_aggregate_id', 'outbox', ['aggregate_id'])
    op.create_index('idx_outbox_status', 'outbox', ['status'])

def downgrade() -> None:
    op.drop_table('outbox')
    op.drop_table('payments')
