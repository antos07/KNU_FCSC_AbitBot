"""Create limit_chat_member procedure

Revision ID: 207864a00f24
Revises: 72c42b9369b1
Create Date: 2023-11-01 12:44:30.968855+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "207864a00f24"
down_revision = "72c42b9369b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
CREATE PROCEDURE limit_chat_member(chat_id bigint, user_id bigint, since timestamp = current_timestamp, limitation_type varchar(10) = 'ban')
    LANGUAGE plpgsql
AS
$$
DECLARE limitation_id int;
BEGIN 
    SELECT id FROM chat_member_limitation_types WHERE name=limitation_type INTO limitation_id;
    IF limitation_id ISNULL 
    THEN
        INSERT INTO chat_member_limitation_types(name) 
        VALUES (limitation_type) 
        RETURNING id INTO limitation_id;
    END IF;
    INSERT INTO chat_member_limitations(chat_id, user_id, start, type_id) 
    VALUES (chat_id, user_id, since, limitation_id);
END 
$$
    """
    )


def downgrade() -> None:
    op.execute(
        "DROP PROCEDURE limit_chat_member(bigint, bigint, timestamp, varchar(10))"
    )
