"""Added time fields in sleap model

Revision ID: 97cc999e7c8a
Revises: ad9d4372a1ed
Create Date: 2024-03-31 12:57:09.122774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97cc999e7c8a'
down_revision = 'ad9d4372a1ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleap_neural_network', schema=None) as batch_op:
        batch_op.add_column(sa.Column('started_training_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('finished_training_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleap_neural_network', schema=None) as batch_op:
        batch_op.drop_column('finished_training_at')
        batch_op.drop_column('started_training_at')

    # ### end Alembic commands ###