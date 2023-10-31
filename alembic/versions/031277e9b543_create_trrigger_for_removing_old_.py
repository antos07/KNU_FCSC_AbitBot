"""Create trrigger for removing old messages

Revision ID: 031277e9b543
Revises: 29456d627383
Create Date: 2023-10-31 12:07:33.714679+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '031277e9b543'
down_revision = '29456d627383'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION remove_relatively_old_messages()
        RETURNS TRIGGER
        AS
        $$
        BEGIN 
            DELETE FROM messages
            WHERE messages.sent_at < NEW.sent_at - INTERVAL '1 DAY';
            RETURN NEW;
        END 
        $$
        LANGUAGE plpgsql;
        
        CREATE TRIGGER remove_old_messages_on_insert BEFORE INSERT
            ON messages
        EXECUTE PROCEDURE remove_relatively_old_messages();
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER remove_old_messages_on_insert on messages;
        DROP FUNCTION remove_relatively_old_messages;
    """)
