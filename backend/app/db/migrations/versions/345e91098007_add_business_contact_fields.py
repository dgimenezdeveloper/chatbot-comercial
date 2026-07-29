"""add_business_contact_fields

Revision ID: 345e91098007
Revises: 234d80897006
Create Date: 2026-07-29 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '345e91098007'
down_revision: Union[str, None] = '234d80897006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('business', sa.Column('horarios', sa.String(length=255), nullable=True, comment='Horarios de atención'))
    op.add_column('business', sa.Column('contacto', sa.String(length=255), nullable=True, comment='Información de contacto'))

def downgrade() -> None:
    op.drop_column('business', 'contacto')
    op.drop_column('business', 'horarios')