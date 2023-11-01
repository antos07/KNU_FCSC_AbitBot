"""Add create_admin function

Revision ID: f93b4be54dc5
Revises: 4bf0c28ac3a2
Create Date: 2023-11-01 21:22:43.989543+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f93b4be54dc5'
down_revision = '4bf0c28ac3a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE FUNCTION hash_password(password varchar(50)) RETURNS varchar(256)
    LANGUAGE plpgsql
AS 
$$
BEGIN
    RETURN encode(sha256(password::bytea), 'hex');
END 
$$;
    
CREATE PROCEDURE create_admin(email varchar(100), password varchar(50), can_edit_admins bool = FALSE)
    LANGUAGE plpgsql
AS
$$
DECLARE password_hash varchar(256);
BEGIN
    IF length(password) < 8
    THEN
        RAISE 'Password to short. At least 8 symbols required.';
    END IF;
    password_hash = hash_password(password);
    INSERT INTO admins(email, password_hash, can_edit_admins) 
    VALUES 
    (email, password_hash, can_edit_admins);
END
$$
    """)


def downgrade() -> None:
    op.execute("DROP PROCEDURE create_admin(varchar(100), varchar(50), bool);")
    op.execute("DROP FUNCTION hash_password(varchar(50));")
