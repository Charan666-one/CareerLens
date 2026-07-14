"""add resume_text to analysis_states

Revision ID: 055d5f3a29e1
Revises: 993088e694ef
Create Date: 2026-07-14 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '055d5f3a29e1'
down_revision: Union[str, Sequence[str], None] = '993088e694ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('analysis_states', sa.Column('resume_text', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysis_states', 'resume_text')
