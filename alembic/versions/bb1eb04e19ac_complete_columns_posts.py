"""complete-columns-posts

Revision ID: bb1eb04e19ac
Revises: f2061cd064be
Create Date: 2022-03-20 14:12:31.553199

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bb1eb04e19ac'
down_revision = 'f2061cd064be'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'posts',
        sa.Column('published',
                  sa.Boolean(),
                  nullable=False,
                  server_default='TRUE'),
    )
    op.add_column(
        'posts',
        sa.Column('created_at',
                  sa.TIMESTAMP(timezone=True),
                  nullable=False,
                  server_default=sa.text('NOW()')))


def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
