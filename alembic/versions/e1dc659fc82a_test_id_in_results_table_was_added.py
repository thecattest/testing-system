"""test id in results table was added

Revision ID: e1dc659fc82a
Revises: 
Create Date: 2020-04-01 19:35:16.911774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1dc659fc82a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('result', sa.Column('test_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('result', 'test_id')
    # ### end Alembic commands ###