"""rename_columns_english_and_fix_types

Revision ID: e26a6fbe72a2
Revises: 
Create Date: 2026-04-30 17:05:49.796773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e26a6fbe72a2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # rag_stores: español → inglés
    op.alter_column('rag_stores', 'descripcion',
                    new_column_name='description')
    op.alter_column('rag_stores', 'archivos_count',
                    new_column_name='file_count')

    # rag_stores: corregir tipo de id (varchar uuid → uuid nativo)
    op.execute("""
        ALTER TABLE rag_stores
        ALTER COLUMN id TYPE uuid USING id::uuid
    """)

    # rag_stores: corregir nullable de file_count
    op.alter_column('rag_stores', 'file_count', nullable=True)

    # evidence_metadata: renombrar columnas
    op.alter_column('evidence_metadata', 'document_name',
                    new_column_name='gemini_resource_name')
    op.alter_column('evidence_metadata', 'file_ref',
                    new_column_name='gemini_ref')

    # evidence_metadata: agregar updated_at si no existe
    op.execute("""
        ALTER TABLE evidence_metadata
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT now()
    """)

    # evidence_metadata: corregir nullable de status
    op.alter_column('evidence_metadata', 'status', nullable=True)

    # audit_logs: renombrar data → event_data
    op.alter_column('audit_logs', 'data',
                    new_column_name='event_data')

    # sessions: corregir nullable de audit_name
    op.alter_column('sessions', 'audit_name', nullable=False,
                    server_default='')


def downgrade() -> None:
    # sessions
    op.alter_column('sessions', 'audit_name', nullable=True,
                    server_default=None)

    # audit_logs
    op.alter_column('audit_logs', 'event_data',
                    new_column_name='data')

    # evidence_metadata
    op.alter_column('evidence_metadata', 'status', nullable=False)
    op.alter_column('evidence_metadata', 'gemini_ref',
                    new_column_name='file_ref')
    op.alter_column('evidence_metadata', 'gemini_resource_name',
                    new_column_name='document_name')

    # rag_stores
    op.alter_column('rag_stores', 'file_count', nullable=False)
    op.execute("""
        ALTER TABLE rag_stores
        ALTER COLUMN id TYPE varchar(36) USING id::text
    """)
    op.alter_column('rag_stores', 'file_count',
                    new_column_name='archivos_count')
    op.alter_column('rag_stores', 'description',
                    new_column_name='descripcion')
