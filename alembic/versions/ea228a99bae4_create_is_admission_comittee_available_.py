"""Create is_admission_comittee_available() function

Revision ID: ea228a99bae4
Revises: 446f086b71c5
Create Date: 2023-11-01 21:49:13.071939+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea228a99bae4'
down_revision = '446f086b71c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE FUNCTION is_admission_committe_available(chat_id bigint) RETURNS bool
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF (SELECT TRUE 
        WHERE EXISTS(
            SELECT 
            FROM admission_committee_timetable t
            WHERE t.applicant_chat_id = chat_id
              AND t.start_time <= now()::time without time zone
              AND t.end_time > now()::time without time zone)
        )
    THEN
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END 
$$
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION is_admission_committe_available(bigint);")
