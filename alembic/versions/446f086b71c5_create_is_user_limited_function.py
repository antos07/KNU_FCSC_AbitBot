"""Create is_user_limited function

Revision ID: 446f086b71c5
Revises: f93b4be54dc5
Create Date: 2023-11-01 21:35:46.945117+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '446f086b71c5'
down_revision = 'f93b4be54dc5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE FUNCTION is_user_limited(user_id bigint, chat_id bigint) RETURNS bool
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF (SELECT TRUE 
        WHERE EXISTS(
            SELECT 
            FROM chat_member_limitations cml
            WHERE cml.user_id = is_user_limited.user_id
              AND cml.chat_id = is_user_limited.chat_id
              AND (cml."end" ISNULL OR cml."end" > now()))
        )
    THEN
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END 
$$
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION is_user_limited(bigint, bigint);")
