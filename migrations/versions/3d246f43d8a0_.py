"""empty message

Revision ID: 3d246f43d8a0
Revises: 92e29df24ecf
Create Date: 2024-08-23 17:42:17.533981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d246f43d8a0'
down_revision = '92e29df24ecf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.drop_column('eye_color')
        batch_op.drop_column('skin_color')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skin_color', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('eye_color', sa.VARCHAR(length=20), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
