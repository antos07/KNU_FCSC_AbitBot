"""Initial revision

Revision ID: 11a62d74b651
Revises: 
Create Date: 2023-07-30 18:21:29.472592+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11a62d74b651'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('abit_chat_info',
    sa.Column('chat_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('flood_chat_link', sa.String(length=500), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('programs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('guide_url', sa.String(length=500), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('useful_links',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('useful_links')
    op.drop_table('programs')
    op.drop_table('abit_chat_info')
    # ### end Alembic commands ###
