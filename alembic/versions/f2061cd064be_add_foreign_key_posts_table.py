"""add-foreign-key-posts-table

Revision ID: f2061cd064be
Revises: 27f408589540
Create Date: 2022-03-20 13:59:44.233797

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2061cd064be'
down_revision = '27f408589540'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk',
                          source_table='posts',
                          referent_table='users',
                          local_cols=['owner_id'],
                          remote_cols=['id'],
                          ondelete="CASCADE")


def downgrade():
    op.drop_constraint('post_users_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
