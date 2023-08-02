"""Make AbitChatInfo.chat_id a BigInteger

Revision ID: d6c04595643a
Revises: 0ad3332dbeac
Create Date: 2023-08-02 08:05:42.948962+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd6c04595643a'
down_revision = '0ad3332dbeac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('abit_chat_info', 'chat_id',
                    type_=sa.BigInteger)


def downgrade() -> None:
    op.alter_column('abit_chat_info', 'chat_id',
                    type_=sa.Integer)
