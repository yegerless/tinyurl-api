"""Change password to hahsed_password in User model

Revision ID: 92dfbc91f5ed
Revises: 74aa2c0a3d28
Create Date: 2025-03-24 21:34:31.451813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92dfbc91f5ed'
down_revision: Union[str, None] = '74aa2c0a3d28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('hashed_password', sa.String(), nullable=True))
    op.drop_column('user', 'password')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('user', 'hashed_password')
    # ### end Alembic commands ###
