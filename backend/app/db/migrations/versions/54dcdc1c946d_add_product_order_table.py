"""add_product_order_table

Revision ID: 54dcdc1c946d
Revises: 8bc4bdb8bd93
Create Date: 2026-08-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '54dcdc1c946d'
down_revision: Union[str, None] = '8bc4bdb8bd93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = [c['name'] for c in inspector.get_columns('business')]

    if 'tiktok' not in existing_columns:
        op.add_column('business', sa.Column('tiktok', sa.String(length=100), nullable=True, comment='Usuario de TikTok'))
    if 'twitter' not in existing_columns:
        op.add_column('business', sa.Column('twitter', sa.String(length=100), nullable=True, comment='Usuario de X (Twitter)'))

    tables = inspector.get_table_names()
    if 'product_order' not in tables:
        op.create_table(
            'product_order',
            sa.Column('id', sa.Integer(), nullable=False, comment='ID interno autoincremental'),
            sa.Column('business_id', sa.Integer(), nullable=False, comment='Negocio al que pertenece el pedido'),
            sa.Column('user_name', sa.String(length=200), nullable=True, comment='Nombre del cliente'),
            sa.Column('user_phone', sa.String(length=20), nullable=True, comment='Teléfono del cliente'),
            sa.Column('items_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Lista de productos reservados'),
            sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False, comment='Precio total de la reserva'),
            sa.Column('status', sa.String(length=50), nullable=True, server_default='pendiente', comment='Estado del pedido'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='Fecha de creación de la reserva'),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='Fecha de última modificación'),
            sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_product_order_id'), 'product_order', ['id'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if 'product_order' in tables:
        op.drop_index(op.f('ix_product_order_id'), table_name='product_order')
        op.drop_table('product_order')