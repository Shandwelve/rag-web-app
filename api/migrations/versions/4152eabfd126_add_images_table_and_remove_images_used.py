"""add_images_table_and_remove_images_used

Revision ID: 4152eabfd126
Revises: 53e4fe25775
Create Date: 2025-01-28 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "4152eabfd126"
down_revision: Union[str, Sequence[str], None] = "53e4fe25775"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create images table
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("chunk_id", sa.Integer(), nullable=False),
        sa.Column("image_data", sa.Text(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("image_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["file.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_images_chunk_id"), "images", ["chunk_id"], unique=False
    )
    op.create_index(
        op.f("ix_images_file_id"), "images", ["file_id"], unique=False
    )
    
    # Remove images_used column from answers table
    op.drop_column("answers", "images_used")


def downgrade() -> None:
    """Downgrade schema."""
    # Add back images_used column
    op.add_column(
        "answers",
        sa.Column("images_used", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    
    # Drop images table
    op.drop_index(op.f("ix_images_file_id"), table_name="images")
    op.drop_index(op.f("ix_images_chunk_id"), table_name="images")
    op.drop_table("images")
