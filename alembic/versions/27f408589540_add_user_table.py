"""add-user-table

Revision ID: 27f408589540
Revises: b6af95ca9538
Create Date: 2022-03-20 13:49:12.942299

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27f408589540'
down_revision = 'b6af95ca9538'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users', sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at',
                  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'),
                  nullable=False), sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'))


def downgrade():
    op.drop_table('users')
