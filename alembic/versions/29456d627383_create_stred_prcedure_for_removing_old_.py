"""Create stred prcedure for removing old messages

Revision ID: 29456d627383
Revises: cfefd4d290fd
Create Date: 2023-10-31 11:53:22.349426+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '29456d627383'
down_revision = 'cfefd4d290fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE PROCEDURE remove_old_messages()
    LANGUAGE SQL
    AS
    $$
    BEGIN;
        DELETE FROM messages
        WHERE messages.sent_at < NOW() - INTERVAL '1 DAY';
    END;
    $$
    """)


def downgrade() -> None:
    op.execute("""DROP PROCEDURE remove_old_messages();""")
