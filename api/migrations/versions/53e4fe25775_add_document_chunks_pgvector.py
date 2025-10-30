"""Add document_chunks with pgvector

Revision ID: 53e4fe25775
Revises: f4ee5d9f4847
Create Date: 2025-01-27 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback if pgvector is not available during migration loading
    Vector = sa.String  # Will be replaced with actual Vector type in the migration


# revision identifiers, used by Alembic.
revision: str = "53e4fe25775"
down_revision: Union[str, Sequence[str], None] = "f4ee5d9f4847"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create document_chunks table with embedding as ARRAY first, then convert to vector
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("embedding", sa.dialects.postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("chunk_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["file.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create index on file_id for faster lookups
    op.create_index(
        op.f("ix_document_chunks_file_id"), "document_chunks", ["file_id"], unique=False
    )
    
    # Convert the embedding column to vector type using raw SQL
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(384) USING embedding::vector")
    
    # Create vector index for similarity search (using HNSW for better performance)
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding ON document_chunks "
        "USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_document_chunks_embedding", table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_file_id"), table_name="document_chunks")
    op.drop_table("document_chunks")
    op.execute("DROP EXTENSION IF EXISTS vector")
