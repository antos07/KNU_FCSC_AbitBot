"""Fix admission timetable validation triiger

Revision ID: 2dfbbf7f3371
Revises: 2d5fb7625b09
Create Date: 2023-11-01 10:37:13.795680+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2dfbbf7f3371"
down_revision = "2d5fb7625b09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
CREATE OR REPLACE FUNCTION validate_admission_committee_timetable() RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
BEGIN
    RAISE WARNING '%', new;
    IF NEW.start_time > NEW.end_time
        OR (SELECT TRUE
            FROM admission_committee_timetable
            WHERE date = NEW.date
              AND id <> NEW.id
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

CREATE OR REPLACE TRIGGER validate_admission_committee_timetable 
BEFORE INSERT OR UPDATE ON admission_committee_timetable
FOR EACH ROW EXECUTE FUNCTION validate_admission_committee_timetable();
    """
    )


def downgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION validate_admission_committee_timetable() RETURNS TRIGGER
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
    
CREATE OR REPLACE TRIGGER validate_admission_committee_timetable 
BEFORE INSERT OR UPDATE 
ON admission_committee_timetable
EXECUTE FUNCTION validate_admission_committee_timetable();
        """
    )
