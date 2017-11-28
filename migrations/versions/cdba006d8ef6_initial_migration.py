"""initial migration

Revision ID: cdba006d8ef6
Revises: 205a6a56b098
Create Date: 2017-11-25 22:33:21.464000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdba006d8ef6'
down_revision = '205a6a56b098'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    # ### end Alembic commands ###