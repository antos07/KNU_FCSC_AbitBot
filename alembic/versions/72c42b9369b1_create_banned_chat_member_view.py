"""Create banned chat member view

Revision ID: 72c42b9369b1
Revises: 2dfbbf7f3371
Create Date: 2023-11-01 11:18:52.499850+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72c42b9369b1'
down_revision = '2dfbbf7f3371'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE VIEW banned_chat_members AS
SELECT chat_id, user_id, joined, role_id
FROM chat_members
WHERE EXISTS(SELECT *
             FROM chat_member_limitations
             JOIN public.chat_member_limitation_types cmlt on cmlt.id = chat_member_limitations.type_id
             WHERE chat_members.chat_id = chat_member_limitations.chat_id
               AND chat_members.user_id = chat_member_limitations.user_id
               AND (chat_member_limitations."end" ISNULL 
                    OR chat_member_limitations."end" > now())
               AND cmlt.name = 'ban'
             )
 
    """)


def downgrade() -> None:
    op.execute("""DROP VIEW banned_chat_members;""")
