"""Rewrite admission committee timetable model

Revision ID: 377a6160563e
Revises: 631644d659d5
Create Date: 2023-10-30 13:00:46.972420+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '377a6160563e'
down_revision = '631644d659d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admission_committee_timetable',
    sa.Column('applicant_chat_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.ForeignKeyConstraint(['applicant_chat_id'], ['applicant_chats.chat_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('applicant_chat_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admission_committee_timetable')
    # ### end Alembic commands ###