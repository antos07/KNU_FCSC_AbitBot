"""Create is_relatively_old function

Revision ID: c6bebcff0ca3
Revises: 031277e9b543
Create Date: 2023-10-31 13:15:10.040280+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c6bebcff0ca3'
down_revision = '031277e9b543'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE FUNCTION is_relatively_old(t timestamp, relative_to timestamp = NULL)
RETURNS bool
LANGUAGE sql
RETURN t < COALESCE(relative_to, NOW()) - INTERVAL '1 DAY';
    """)

    op.execute("""
create or replace procedure remove_old_messages()
    language sql
as
$$
DELETE
FROM messages
WHERE is_relatively_old(messages.sent_at);
$$;
    """)

    op.execute("""
CREATE OR REPLACE FUNCTION remove_relatively_old_messages() RETURNS TRIGGER
    LANGUAGE plpgsql
AS 
$$
BEGIN
    DELETE
    FROM messages
    WHERE is_relatively_old(messages.sent_at, NEW.sent_at);
    RETURN NEW;
END
$$;

alter function remove_relatively_old_messages() owner to postgres;
""")


def downgrade() -> None:
    op.execute("""
    create or replace procedure remove_old_messages()
        language sql
    as
    $$
    DELETE
    FROM messages
    WHERE messages.sent_at < NOW() - INTERVAL '1 DAY';
    $$;
""")

    op.execute("""
CREATE OR REPLACE FUNCTION remove_relatively_old_messages() RETURNS TRIGGER
    LANGUAGE plpgsql
AS 
$$
BEGIN
    DELETE
    FROM messages
    WHERE messages.sent_at < NEW.sent_at - INTERVAL '1 DAY';
    RETURN NEW;
END
$$;

alter function remove_relatively_old_messages() owner to postgres;
""")
    op.execute("DROP FUNCTION is_relatively_old(timestamp, timestamp);")
