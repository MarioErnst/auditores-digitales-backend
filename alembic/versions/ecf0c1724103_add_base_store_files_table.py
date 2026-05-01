"""add_base_store_files_table

Revision ID: ecf0c1724103
Revises: e26a6fbe72a2
Create Date: 2026-04-30 23:03:16.694256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ecf0c1724103'
down_revision: Union[str, Sequence[str], None] = 'e26a6fbe72a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'base_store_files',
        sa.Column('id', postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gemini_resource_name', sa.String(), nullable=True),
        sa.Column('store_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False,
                  server_default='processing'),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text('now()'),
                  nullable=False),
    )
    op.create_index('ix_base_store_files_store_name',
                    'base_store_files', ['store_name'])


def downgrade() -> None:
    op.drop_index('ix_base_store_files_store_name')
    op.drop_table('base_store_files')
