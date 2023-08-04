"""Make pinguin a penguin (fix typo)

Revision ID: 15f5768bb6cd
Revises: 943147f1b7d5
Create Date: 2023-08-04 13:13:55.378320+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '15f5768bb6cd'
down_revision = '943147f1b7d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('sent_pinguin_records', 'sent_penguin_records')

    # rename sent_pinguin_records_pkey to sent_penguin_records_pkey
    op.drop_constraint('sent_pinguin_records_pkey', 'sent_penguin_records',
                       type_='primary')
    op.create_primary_key(
        constraint_name='sent_penguin_records_pkey',
        table_name='sent_penguin_records',
        columns=['id'],
    )

    # rename sent_pinguin_records_chat_member_id_fkey to
    # sent_pinguin_records_chat_member_id_fkey
    op.drop_constraint('sent_pinguin_records_chat_member_id_fkey',
                       'sent_penguin_records',
                       type_='foreignkey')
    op.create_foreign_key(
        constraint_name='sent_penguin_records_chat_member_id_fkey',
        source_table='sent_penguin_records',
        referent_table='chat_members',
        local_cols=['chat_member_id'],
        remote_cols=['id'],
    )


def downgrade() -> None:
    op.rename_table('sent_penguin_records', 'sent_pinguin_records')

    # rename sent_penguin_records_pkey to sent_pinguin_records_pkey
    op.drop_constraint('sent_penguin_records_pkey', 'sent_pinguin_records',
                       type_='primary')
    op.create_primary_key(
        constraint_name='sent_pinguin_records_pkey',
        table_name='sent_pinguin_records',
        columns=['id'],
    )

    # rename sent_pinguin_records_chat_member_id_fkey to
    # sent_pinguin_records_chat_member_id_fkey
    op.drop_constraint('sent_penguin_records_chat_member_id_fkey',
                       'sent_pinguin_records',
                       type_='foreignkey')
    op.create_foreign_key(
        constraint_name='sent_pinguin_records_chat_member_id_fkey',
        source_table='sent_pinguin_records',
        referent_table='chat_members',
        local_cols=['chat_member_id'],
        remote_cols=['id'],
    )
