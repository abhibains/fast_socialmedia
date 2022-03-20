"""add-content-column-to-post

Revision ID: b6af95ca9538
Revises: a5ebbda7e495
Create Date: 2022-03-20 13:37:23.115716

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b6af95ca9538'
down_revision = 'a5ebbda7e495'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))


def downgrade():
    op.drop_column('posts', 'content')
