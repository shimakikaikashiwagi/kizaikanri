"""add tool_type to SurveyingTool

Revision ID: 40525eae9299
Revises: 5de9a83e0cdd
Create Date: 2025-05-16 09:26:54.006000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40525eae9299'
down_revision = '5de9a83e0cdd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('surveying_tools', schema=None) as batch_op:
        # 1. 一旦nullable=Trueで追加し、デフォルト値も設定する（例：空文字や"unknown"など）
        batch_op.add_column(sa.Column('tool_type', sa.String(length=100), nullable=False, server_default='unknown'))
    # 2. 必要ならserver_defaultを解除する（optional）
    with op.batch_alter_table('surveying_tools', schema=None) as batch_op:
        batch_op.alter_column('tool_type', server_default=None)


def downgrade():
    with op.batch_alter_table('surveying_tools', schema=None) as batch_op:
        batch_op.drop_column('tool_type')


    # ### end Alembic commands ###
