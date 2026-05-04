"""add users

Revision ID: 4f2b8d1c9a7e
Revises: ad7d2109108f
Create Date: 2026-11-19 15:02:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f2b8d1c9a7e'
down_revision = 'ad7d2109108f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )


def downgrade():
    op.drop_table('users')
