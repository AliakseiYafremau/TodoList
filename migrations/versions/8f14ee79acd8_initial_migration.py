"""Initial migration

Revision ID: 8f14ee79acd8
Revises: 
Create Date: 2024-11-16 14:53:04.927753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8f14ee79acd8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'another_field')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('another_field', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
