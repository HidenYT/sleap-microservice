"""Added training config field into sleap model

Revision ID: ad9d4372a1ed
Revises: 574daf9df370
Create Date: 2024-03-31 12:46:16.362617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad9d4372a1ed'
down_revision = '574daf9df370'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleap_neural_network', schema=None) as batch_op:
        batch_op.add_column(sa.Column('training_config', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleap_neural_network', schema=None) as batch_op:
        batch_op.drop_column('training_config')

    # ### end Alembic commands ###