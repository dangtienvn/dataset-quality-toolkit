"""create rag documents table

Revision ID: 002
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "rag_documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String()),
        sa.Column("created_at", sa.DateTime())
    )

def downgrade():
    op.drop_table("rag_documents")

# Updated audit checkpoint 2026-08-27 17:45
