"""edit column type description product

Revision ID: 9fa3296993ad
Revises: 9120d915f2c6
Create Date: 2020-01-16 08:44:20.476893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fa3296993ad'
down_revision = '9120d915f2c6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('products', 'description', existing_type=sa.String(128), type_=sa.String())


def downgrade():
    pass
