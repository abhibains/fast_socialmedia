"""create_post_table

Revision ID: a5ebbda7e495
Revises: 
Create Date: 2022-03-20 10:45:34.707787

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a5ebbda7e495'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():  #handles the changes and
    op.create_table(
        'posts', sa.Column('id',
                           sa.Integer(),
                           nullable=False,
                           primary_key=True),
        sa.Column('title', sa.String(), nullable=False))


def downgrade():  # handles rolling the changes back
    op.drop_table('posts')
