"""Create admission timetable validation triiger

Revision ID: 63920cdc14d4
Revises: c6bebcff0ca3
Create Date: 2023-11-01 10:05:53.825593+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63920cdc14d4'
down_revision = 'c6bebcff0ca3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE FUNCTION validate_admission_committee_timetable() RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.start_time > NEW.end_time
        OR (SELECT *
            FROM admission_committee_timetable
            WHERE date = NEW.date
              AND applicant_chat_id = NEW.applicant_chat_id
              AND (start_time <= NEW.start_time
                       AND NEW.start_time < end_time
                OR end_time <= NEW.end_time)
              AND NEW.end_time > start_time)
    THEN
        RAISE 'Impossible or overlapping timetable record';
    END IF;
    RETURN NEW;
END
$$;

CREATE TRIGGER validate_admission_committee_timetable 
BEFORE INSERT OR UPDATE 
ON admission_committee_timetable
EXECUTE FUNCTION validate_admission_committee_timetable();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER validate_admission_committee_timetable;")
    op.execute("DROP FUNCTION validate_admission_committee_timetable();")
