"""add_cascade_delete_to_answers

Revision ID: e1e3bcdd3e52
Revises: 4152eabfd126
Create Date: 2025-01-28 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1e3bcdd3e52"
down_revision: Union[str, Sequence[str], None] = "4152eabfd126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign key constraint
    op.drop_constraint('answers_question_id_fkey', 'answers', type_='foreignkey')
    
    # Add foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'answers_question_id_fkey',
        'answers',
        'questions',
        ['question_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop CASCADE foreign key constraint
    op.drop_constraint('answers_question_id_fkey', 'answers', type_='foreignkey')
    
    # Add back original foreign key constraint without CASCADE
    op.create_foreign_key(
        'answers_question_id_fkey',
        'answers',
        'questions',
        ['question_id'],
        ['id']
    )
