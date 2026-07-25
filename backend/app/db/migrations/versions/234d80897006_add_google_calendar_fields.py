"""add_google_calendar_fields

Revision ID: 234d80897006
Revises: d9d7dbca55b1
Create Date: 2026-07-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '234d80897006'
down_revision: Union[str, None] = 'd9d7dbca55b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('business', sa.Column('google_calendar_id', sa.String(length=255), nullable=True, comment='ID del calendario secundario de Google'))
    op.add_column('appointment', sa.Column('google_event_id', sa.String(length=255), nullable=True, comment='ID del evento en Google Calendar'))

def downgrade() -> None:
    op.drop_column('appointment', 'google_event_id')
    op.drop_column('business', 'google_calendar_id')