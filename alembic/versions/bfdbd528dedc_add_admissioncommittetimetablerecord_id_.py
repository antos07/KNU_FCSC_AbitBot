"""Add AdmissionCommitteTimetableRecord.id field as the PK

Revision ID: bfdbd528dedc
Revises: 2234d59848c3
Create Date: 2023-08-05 21:18:25.975257+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bfdbd528dedc'
down_revision = '2234d59848c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('admission_committe_timetable_pkey',
                       'admission_committe_timetable', type_='primary')
    op.add_column('admission_committe_timetable',
                  sa.Column('id', sa.Integer(), nullable=False,
                            primary_key=True))


def downgrade() -> None:
    op.drop_constraint('admission_committe_timetable_pkey',
                       'admission_committe_info', type_='primary')
    op.drop_column('admission_committe_timetable', 'id')
    op.create_primary_key('admission_committe_timetable_pkey',
                          'admission_committe_timetable', ['id'])
